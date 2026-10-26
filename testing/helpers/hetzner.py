import base64
import datetime
import json
import os
import shutil
import tempfile
import textwrap
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bucket import FakeBucket
from stubs import executable

SECRET = 'resolved-s3cr3t-value'
SERVER_NUMBER = 4242
IPV6_NET = '2a01:4f8:111:4221::'
CHOSEN = 3100777
CHOSEN_HOURLY = '0.1763'
TRANSACTION = 'B20261026-1'


def listing(id, cpu, hourly, setup='0.0000', datacenter='FSN1-DC1', monthly='110.0000'):
    return {'id': id, 'name': 'Server Auction', 'cpu': cpu, 'datacenter': datacenter, 'dist': ['Rescue system'],
            'price': monthly, 'price_vat': monthly, 'price_hourly': hourly, 'price_hourly_vat': hourly,
            'price_setup': setup, 'price_setup_vat': setup, 'fixed_price': False}


def auction():
    return [listing(3100001, 'AMD Ryzen 7 7700', '0.1000'),
            listing(3100002, 'Intel Core i5-12400F', '0.1100'),
            listing(3100003, 'Intel Core i7-6700', '0.1150'),
            listing(3100004, 'Intel Core i5-13500', '0.1200', setup='39.0000'),
            listing(3100005, 'Intel Core i5-12500', None),
            listing(3100006, 'Intel Core i9-13900', '0.2949'),
            listing(CHOSEN, 'Intel Core i5-12500', CHOSEN_HOURLY, datacenter='FSN1-DC4', monthly='109.9000'),
            listing(3100008, 'Intel Xeon E5-1650V3', '0.0900')]


PUBLIC_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINWoPn30OFsbwWfmUhgb6N/ORlz840KoDcMKq315dHRV test@machines\n'
DEDICATED_PRIVATE = 'dedicated-private-key-body\n'
PERSONAL_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPersonalKeyOfTheUserNeverToBeSentAnywhere0 user@laptop\n'
PERSONAL_PRIVATE = 'personal-private-key-body\n'

SPYING_STUB = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys, time
    name = os.path.basename(sys.argv[0])
    args = sys.argv[1:]
    spy = os.environ['MACHINES_TEST_SPY']
    with open(os.path.join(spy, name), 'a') as f:
        f.write(json.dumps(args) + '\\n')
    with open(os.path.join(spy, 'sequence'), 'a') as f:
        f.write(json.dumps([name] + args) + '\\n')
    def scripted():
        for n, rule in enumerate(filter(None, os.environ.get('STUB_SEQ', '').split(';'))):
            head, _, series = rule.partition('=')
            tool, _, word = head.partition(':')
            if tool != name or not any(word in a for a in args):
                continue
            counter = os.path.join(spy, 'seq-%d' % n)
            try:
                with open(counter) as f:
                    i = int(f.read())
            except OSError:
                i = 0
            with open(counter, 'w') as f:
                f.write(str(i + 1))
            items = series.split('|')
            code, _, out = items[min(i, len(items) - 1)].partition(':')
            if out:
                print(out)
            sys.exit(int(code))
    def matches(var):
        for rule in filter(None, os.environ.get(var, '').split(',')):
            tool, _, word = rule.partition(':')
            if tool == name and any(word in a for a in args):
                return True
        return False
    if matches('STUB_HANG'):
        time.sleep(60)
    if name == 'ssh' and any('bucket.env' in a for a in args):
        with open(os.path.join(spy, 'ssh-stdin'), 'a') as f:
            f.write(sys.stdin.read())
    if matches('STUB_FAIL'):
        sys.exit(1)
    scripted()
    if name == 'scp' and any(a.endswith('/run/out/.') for a in args) and os.path.isdir(args[-1]):
        with open(os.path.join(args[-1], 'soak.md'), 'w') as f:
            f.write('verdict\\n')
    if name == 'ssh' and any('libgl1-mesa-dri' in a for a in args):
        print('25.0.7-2')
    if name == 'terraform' and 'output' in args:
        print(json.dumps({'ipv6_address': {'value': '2a01:4f8:c0c:1::1'}, 'ipv4_address': {'value': '192.0.2.7'}}))
    ''')

SECRET_RUN = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    args = sys.argv[1:]
    with open(os.path.join(os.environ['MACHINES_TEST_SPY'], 'secret-run'), 'a') as f:
        f.write(json.dumps(args) + '\\n')
    env = dict(os.environ)
    while args and args[0] != '--':
        if args[0] == '--env':
            env[args[1].split('=', 1)[0]] = '%s'
            args = args[2:]
        else:
            args = args[1:]
    os.execvpe(args[1], args[1:], env)
    ''') % SECRET


class Hetzner:
    """A stand-in for Robot and the Cloud API: it records every request and answers like them."""

    def __init__(self, market=None, server_ip=None, key_known=True, earliest=None, revoke_refused=False, spy=None):
        self.requests = []
        self.spy = spy
        self.earliest = earliest or datetime.date.today().isoformat()
        self.revoke_refused = revoke_refused
        self.booked = None
        self.cancelled = False
        self.market = auction() if market is None else market
        self.server_ip = server_ip
        self.key_known = key_known
        hetzner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _answer(self, method):
                length = int(self.headers.get('Content-Length') or 0)
                body = self.rfile.read(length).decode() if length else ''
                hetzner.requests.append({'method': method, 'path': self.path,
                                         'form': urllib.parse.parse_qs(body),
                                         'auth': self.headers.get('Authorization', '')})
                if hetzner.spy:
                    entry = ['robot', method, urllib.parse.urlparse(self.path).path]
                    entry += urllib.parse.parse_qs(body).get('cancellation_date', [])
                    with open(os.path.join(hetzner.spy, 'sequence'), 'a') as f:
                        f.write(json.dumps(entry) + '\n')
                status, answer = hetzner.answer(method, self.path, hetzner.requests[-1]['form'])
                data = json.dumps(answer).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                self._answer('GET')

            def do_POST(self):
                self._answer('POST')

            def do_DELETE(self):
                self._answer('DELETE')

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = 'http://127.0.0.1:%d' % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def answer(self, method, path, form=None):
        path = urllib.parse.urlparse(path).path
        if path == '/robot/order/server_market/product':
            return (200, [{'product': p} for p in self.market]) if self.market else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path.startswith('/robot/order/server_market/product/'):
            found = [p for p in self.market if str(p['id']) == path.rsplit('/', 1)[1]]
            return (200, {'product': found[0]}) if found else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path.startswith('/robot/key/') and method == 'GET':
            return (200, {'key': {'fingerprint': path.rsplit('/', 1)[1]}}) if self.key_known else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path == '/robot/key' and method == 'POST':
            self.key_known = True
            return 201, {'key': {'name': 'botropolis-machines'}}
        if path == '/robot/order/server_market/transaction' and method == 'POST':
            if not self.key_known:
                return 400, {'error': {'status': 400, 'code': 'INVALID_INPUT', 'message': 'invalid input',
                                       'missing': None, 'invalid': ['authorized_key']}}
            return 201, {'transaction': {'id': TRANSACTION, 'status': 'in process', 'server_number': None, 'server_ip': None}}
        if path == '/robot/order/server_market/transaction/' + TRANSACTION:
            return 200, {'transaction': {'id': TRANSACTION, 'status': 'ready',
                                         'server_number': SERVER_NUMBER, 'server_ip': self.server_ip}}
        if path == '/robot/server/%d' % SERVER_NUMBER and method == 'GET':
            return 200, {'server': {'server_number': SERVER_NUMBER, 'server_ip': self.server_ip, 'server_ipv6_net': IPV6_NET}}
        if path == '/robot/server/%d/cancellation' % SERVER_NUMBER:
            return self.cancellation(method, (form or {}).get('cancellation_date', [''])[0])
        if path == '/cloud/server_types':
            return 200, {'server_types': [{'name': 'cx33', 'prices': [
                {'location': 'nbg1', 'price_hourly': {'net': '0.0090000000', 'gross': '0.0107100000'},
                 'price_monthly': {'net': '5.4900000000', 'gross': '6.5331000000'}}]}]}
        return 404, {'error': {'status': 404, 'code': 'NOT_FOUND', 'path': path}}

    def cancellation(self, method, date):
        conflict = {'error': {'status': 409, 'code': 'CONFLICT', 'message': 'The server is already cancelled'}}
        if method == 'POST':
            if self.booked or self.cancelled:
                return 409, conflict
            if date == 'now':
                self.cancelled = True
            else:
                self.booked = date
        if method == 'DELETE':
            if self.revoke_refused:
                return 409, {'error': {'status': 409, 'code': 'CONFLICT', 'message': 'The cancellation cannot be revoked'}}
            self.booked = None
            return 200, {}
        return 200, {'cancellation': {'server_number': SERVER_NUMBER, 'earliest_cancellation_date': self.earliest,
                                      'cancelled': bool(self.booked or self.cancelled), 'reservation_possible': False,
                                      'reservation': False,
                                      'cancellation_date': self.booked or (self.earliest if self.cancelled else None)}}

    def sent(self, method, path):
        return [r for r in self.requests if r['method'] == method and urllib.parse.urlparse(r['path']).path == path]

    def orders(self, test):
        return [r for r in self.sent('POST', '/robot/order/server_market/transaction')
                if (r['form'].get('test') == ['true']) == test]


class Bench:
    """A temporary top with stubbed tools, a fake Hetzner, a home with a public key and a typed answer."""

    def __init__(self, typed='', dedicated_key=True, bucket=None, **hetzner):
        self.top = tempfile.mkdtemp()
        self.spy = os.path.join(self.top, 'spy')
        self.bin = os.path.join(self.top, 'bin')
        self.home = os.path.join(self.top, 'home')
        self.state = os.path.join(self.top, 'state')
        self.out = os.path.join(self.top, 'out')
        for d in (self.spy, self.bin, os.path.join(self.home, '.ssh'), self.state):
            os.makedirs(d)
        for name in ('terraform', 'ssh', 'scp', 'ip'):
            executable(os.path.join(self.bin, name), SPYING_STUB)
        executable(os.path.join(self.bin, 'secret-run'), SECRET_RUN)
        self.dedicated = os.path.join(self.home, '.ssh', 'botropolis-machines')
        self.personal = os.path.join(self.home, '.ssh', 'id_ed25519')
        for path, text in ((self.personal + '.pub', PERSONAL_KEY), (self.personal, PERSONAL_PRIVATE)):
            with open(path, 'w') as f:
                f.write(text)
        if dedicated_key:
            for path, text in ((self.dedicated + '.pub', PUBLIC_KEY), (self.dedicated, DEDICATED_PRIVATE)):
                with open(path, 'w') as f:
                    f.write(text)
            os.chmod(self.dedicated, 0o600)
        self.tty = os.path.join(self.top, 'tty')
        with open(self.tty, 'w') as f:
            f.write(typed + '\n')
        self.build = os.path.join(self.top, 'build')
        self.corpus = os.path.join(self.top, 'demo')
        self.stager = os.path.join(self.top, 'botropolis-demo')
        self.script = os.path.join(self.top, 'shortcut-test')
        for d in (self.build, self.corpus):
            os.makedirs(d)
        for f in (self.stager, self.script):
            executable(f, '#!/bin/sh\n')
        self.history = os.path.join(self.top, 'synthetic', '.claude')
        for project, session in (('-p1', 's1'), ('-p2', 's2'), ('-p2', 's3')):
            os.makedirs(os.path.join(self.history, 'projects', project), exist_ok=True)
            with open(os.path.join(self.history, 'projects', project, session + '.jsonl'), 'w') as f:
                f.write('{}\n')
        self.real_history = os.path.join(self.home, '.claude')
        os.makedirs(os.path.join(self.real_history, 'projects'))
        self.hetzner = Hetzner(spy=self.spy, **hetzner)
        self.bucket = FakeBucket({SECRET: SECRET}, spy=self.spy, **dict({'exit': '0'}, **(bucket or {})))

    def env(self, **extra):
        return dict(os.environ,
                    PATH=self.bin + os.pathsep + os.environ['PATH'],
                    HOME=self.home,
                    XDG_STATE_HOME=self.state,
                    XDG_CACHE_HOME=os.path.join(self.top, 'cache'),
                    MACHINES_TEST_SPY=self.spy,
                    MACHINES_ROBOT_URL=self.hetzner.url + '/robot',
                    MACHINES_HCLOUD_URL=self.hetzner.url + '/cloud',
                    MACHINES_TTY=self.tty,
                    **dict({'MACHINES_POLL_SECONDS': '0'}, **extra))

    def calls(self, tool):
        try:
            with open(os.path.join(self.spy, tool)) as f:
                return [json.loads(line) for line in f]
        except OSError:
            return []

    def every_argv(self):
        return [a for tool in os.listdir(self.spy) if tool not in ('sequence', 'ssh-stdin') and not tool.startswith('seq-')
                for argv in self.calls(tool) for a in argv]

    def private_bodies(self):
        bodies = []
        for path in (self.dedicated, self.personal):
            try:
                with open(path) as f:
                    bodies += [line.strip() for line in f if line.strip() and 'PRIVATE KEY-----' not in line]
            except OSError:
                pass
        return bodies

    def leaks(self):
        """Every argv, form value and file the runner wrote that holds a line of a private key."""
        found = [a for a in self.every_argv() for b in self.private_bodies() if b in a]
        found += [v for r in self.hetzner.requests for vs in r['form'].values() for v in vs
                  for b in self.private_bodies() if b in v]
        for top in (self.state, self.out):
            for d, _, files in os.walk(top):
                for name in files:
                    with open(os.path.join(d, name), errors='replace') as f:
                        text = f.read()
                    found += [os.path.join(d, name) for b in self.private_bodies() if b in text]
        return found

    def uploaded_keys(self):
        return [r['form'].get('data', [''])[0] for r in self.hetzner.sent('POST', '/robot/key')]

    def close(self):
        self.hetzner.close()
        self.bucket.close()
        shutil.rmtree(self.top, ignore_errors=True)


def basic(user, password):
    return 'Basic ' + base64.b64encode(('%s:%s' % (user, password)).encode()).decode()
