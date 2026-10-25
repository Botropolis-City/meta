import base64
import json
import os
import shutil
import tempfile
import textwrap
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from stubs import executable

SECRET = 'resolved-s3cr3t-value'
SERVER_NUMBER = 4242
IPV6_NET = '2a01:4f8:111:4221::'
PUBLIC_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINWoPn30OFsbwWfmUhgb6N/ORlz840KoDcMKq315dHRV test@machines\n'

SPYING_STUB = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys, time
    name = os.path.basename(sys.argv[0])
    args = sys.argv[1:]
    with open(os.path.join(os.environ['MACHINES_TEST_SPY'], name), 'a') as f:
        f.write(json.dumps(args) + '\\n')
    def matches(var):
        for rule in filter(None, os.environ.get(var, '').split(',')):
            tool, _, word = rule.partition(':')
            if tool == name and any(word in a for a in args):
                return True
        return False
    if matches('STUB_HANG'):
        time.sleep(60)
    if matches('STUB_FAIL'):
        sys.exit(1)
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

    def __init__(self, hourly_net='0.0700', setup_net='0.0000', server_ip=None, key_known=True):
        self.requests = []
        self.hourly_net = hourly_net
        self.setup_net = setup_net
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
                status, answer = hetzner.answer(method, self.path)
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

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = 'http://127.0.0.1:%d' % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def answer(self, method, path):
        path = urllib.parse.urlparse(path).path
        if path == '/robot/order/server/product/EX44':
            price = {'net': '45.0000', 'gross': '53.5500', 'hourly_net': self.hourly_net, 'hourly_gross': self.hourly_net}
            return 200, {'product': {'id': 'EX44', 'name': 'Dedicated Root Server EX44',
                                     'dist': ['Debian 12 base', 'Arch Linux latest minimal'],
                                     'location': ['FSN1', 'NBG1'],
                                     'prices': [{'location': 'FSN1', 'price': price,
                                                 'price_setup': {'net': self.setup_net, 'gross': self.setup_net}}]}}
        if path.startswith('/robot/key/') and method == 'GET':
            return (200, {'key': {'fingerprint': path.rsplit('/', 1)[1]}}) if self.key_known else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path == '/robot/key' and method == 'POST':
            return 201, {'key': {'name': 'botropolis-machines'}}
        if path == '/robot/order/server/transaction' and method == 'POST':
            return 201, {'transaction': {'id': 'B20261025-1', 'status': 'in process', 'server_number': None, 'server_ip': None}}
        if path == '/robot/order/server/transaction/B20261025-1':
            return 200, {'transaction': {'id': 'B20261025-1', 'status': 'ready',
                                         'server_number': SERVER_NUMBER, 'server_ip': self.server_ip}}
        if path == '/robot/server/%d' % SERVER_NUMBER and method == 'GET':
            return 200, {'server': {'server_number': SERVER_NUMBER, 'server_ip': self.server_ip, 'server_ipv6_net': IPV6_NET}}
        if path == '/robot/server/%d/cancellation' % SERVER_NUMBER and method == 'POST':
            return 200, {'cancellation': {'server_number': SERVER_NUMBER, 'cancelled': True}}
        if path == '/cloud/server_types':
            return 200, {'server_types': [{'name': 'cx33', 'prices': [
                {'location': 'nbg1', 'price_hourly': {'net': '0.0090000000', 'gross': '0.0107100000'},
                 'price_monthly': {'net': '5.4900000000', 'gross': '6.5331000000'}}]}]}
        return 404, {'error': {'status': 404, 'code': 'NOT_FOUND', 'path': path}}

    def sent(self, method, path):
        return [r for r in self.requests if r['method'] == method and urllib.parse.urlparse(r['path']).path == path]

    def orders(self, test):
        return [r for r in self.sent('POST', '/robot/order/server/transaction')
                if (r['form'].get('test') == ['true']) == test]


class Bench:
    """A temporary top with stubbed tools, a fake Hetzner, a home with a public key and a typed answer."""

    def __init__(self, typed='', **hetzner):
        self.top = tempfile.mkdtemp()
        self.spy = os.path.join(self.top, 'spy')
        self.bin = os.path.join(self.top, 'bin')
        self.home = os.path.join(self.top, 'home')
        self.state = os.path.join(self.top, 'state')
        self.out = os.path.join(self.top, 'out')
        for d in (self.spy, self.bin, os.path.join(self.home, '.ssh'), self.state):
            os.makedirs(d)
        for name in ('terraform', 'ssh', 'scp'):
            executable(os.path.join(self.bin, name), SPYING_STUB)
        executable(os.path.join(self.bin, 'secret-run'), SECRET_RUN)
        with open(os.path.join(self.home, '.ssh', 'id_ed25519.pub'), 'w') as f:
            f.write(PUBLIC_KEY)
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
        self.hetzner = Hetzner(**hetzner)

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
                    MACHINES_POLL_SECONDS='0',
                    **extra)

    def calls(self, tool):
        try:
            with open(os.path.join(self.spy, tool)) as f:
                return [json.loads(line) for line in f]
        except OSError:
            return []

    def every_argv(self):
        return [a for tool in os.listdir(self.spy) for argv in self.calls(tool) for a in argv]

    def close(self):
        self.hetzner.close()
        shutil.rmtree(self.top, ignore_errors=True)


def basic(user, password):
    return 'Basic ' + base64.b64encode(('%s:%s' % (user, password)).encode()).decode()
