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

    def __init__(self, market=None, server_ip=None, key_known=True):
        self.requests = []
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
        if path == '/robot/order/server_market/product':
            return (200, [{'product': p} for p in self.market]) if self.market else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path.startswith('/robot/order/server_market/product/'):
            found = [p for p in self.market if str(p['id']) == path.rsplit('/', 1)[1]]
            return (200, {'product': found[0]}) if found else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path.startswith('/robot/key/') and method == 'GET':
            return (200, {'key': {'fingerprint': path.rsplit('/', 1)[1]}}) if self.key_known else (404, {'error': {'status': 404, 'code': 'NOT_FOUND'}})
        if path == '/robot/key' and method == 'POST':
            return 201, {'key': {'name': 'botropolis-machines'}}
        if path == '/robot/order/server_market/transaction' and method == 'POST':
            return 201, {'transaction': {'id': TRANSACTION, 'status': 'in process', 'server_number': None, 'server_ip': None}}
        if path == '/robot/order/server_market/transaction/' + TRANSACTION:
            return 200, {'transaction': {'id': TRANSACTION, 'status': 'ready',
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
        return [r for r in self.sent('POST', '/robot/order/server_market/transaction')
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
