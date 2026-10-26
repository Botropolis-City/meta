import hashlib
import io
import json
import os
import re
import sys
import tarfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'machines'))
from s3 import canonical_request, signature  # noqa: E402

AUTH = re.compile(r'AWS4-HMAC-SHA256 Credential=([^/]+)/(\d{8})/([^/]+)/s3/aws4_request, '
                  r'SignedHeaders=([^,]+), Signature=([0-9a-f]{64})$')


def report_tarball(files=None):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as tar:
        for name, text in (files or {'soak.md': 'verdict from the bucket\n'}).items():
            body = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(body)
            tar.addfile(info, io.BytesIO(body))
    return data.getvalue()


class FakeBucket:
    """A stand-in for an R2 bucket: it checks every SigV4 signature and records every request.

    For the laptop's half it can answer any run's exit and report as a box would have uploaded them:
    exit_after GETs of an exit object answer 404 before `exit` does; the first fail_reports GETs of a
    report answer 500 (or every one, with fail_reports=-1); refuse_puts PUTs answer 500 first.
    """

    def __init__(self, secrets, exit=None, exit_after=0, report=True, fail_reports=0, refuse_puts=0, spy=None):
        self.secrets = secrets
        self.objects = {}
        self.requests = []
        self.exit, self.exit_after, self.report = exit, exit_after, report
        self.fail_reports, self.refuse_puts, self.spy = fail_reports, refuse_puts, spy
        self.lock = threading.Lock()
        bucket = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _answer(self, method):
                length = int(self.headers.get('Content-Length') or 0)
                body = self.rfile.read(length) if length else b''
                status, answer = bucket.answer(method, self.path, self.headers, body)
                self.send_response(status)
                self.send_header('Content-Length', str(len(answer)))
                self.end_headers()
                self.wfile.write(answer)

            def do_GET(self):
                self._answer('GET')

            def do_PUT(self):
                self._answer('PUT')

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = 'http://127.0.0.1:%d/soak-reports' % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def verify(self, method, path, headers, body):
        match = AUTH.match(headers.get('Authorization', ''))
        if not match or match.group(1) not in self.secrets:
            return None
        key_id, _, region, signed, given = match.groups()
        names = signed.split(';')
        if 'host' not in names or 'x-amz-date' not in names or headers.get('x-amz-content-sha256') is None:
            return None
        if headers['x-amz-content-sha256'] != hashlib.sha256(body).hexdigest():
            return None
        canonical, _ = canonical_request(method, urllib.parse.unquote(urllib.parse.urlsplit(path).path), {},
                                         {n: headers[n] for n in names}, headers['x-amz-content-sha256'])
        good = signature(self.secrets[key_id], headers['x-amz-date'], region, 's3', canonical)
        return key_id if good == given else None

    def answer(self, method, path, headers, body):
        key = urllib.parse.unquote(urllib.parse.urlsplit(path).path).split('/', 2)[2]
        key_id = self.verify(method, path, headers, body)
        with self.lock:
            self.requests.append({'method': method, 'key': key, 'key_id': key_id, 'size': len(body)})
            if self.spy:
                with open(os.path.join(self.spy, 'sequence'), 'a') as f:
                    f.write(json.dumps(['bucket', method, key]) + '\n')
            if key_id is None:
                return 403, b'<Error><Code>SignatureDoesNotMatch</Code></Error>'
            if method == 'PUT':
                if self.refuse_puts:
                    self.refuse_puts -= 1
                    return 500, b'<Error><Code>InternalError</Code></Error>'
                self.objects[key] = body
                return 200, b''
            if key in self.objects:
                return 200, self.objects[key]
            if key.endswith('/exit') and self.exit is not None:
                if self.exit_after:
                    self.exit_after -= 1
                    return 404, b'<Error><Code>NoSuchKey</Code></Error>'
                return 200, self.exit.encode() + b'\n'
            if key.endswith('/report.tar.gz') and self.report:
                if self.fail_reports:
                    self.fail_reports -= 1 if self.fail_reports > 0 else 0
                    return 500, b'<Error><Code>InternalError</Code></Error>'
                return 200, report_tarball()
            return 404, b'<Error><Code>NoSuchKey</Code></Error>'

    def sent(self, method, suffix=''):
        with self.lock:
            return [r for r in self.requests if r['method'] == method and r['key'].endswith(suffix)]
