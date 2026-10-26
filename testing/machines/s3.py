import datetime
import hashlib
import hmac
import urllib.error
import urllib.parse
import urllib.request

UNRESERVED = '-_.~'


def uri_encode(text, encode_slash=True):
    return urllib.parse.quote(text, safe=UNRESERVED + ('' if encode_slash else '/'))


def canonical_request(method, path, query, headers, payload_hash):
    names = sorted(k.lower() for k in headers)
    lowered = {k.lower(): ' '.join(str(v).split()) for k, v in headers.items()}
    signed = ';'.join(names)
    canonical = '\n'.join([
        method,
        uri_encode(path, encode_slash=False),
        '&'.join('%s=%s' % (uri_encode(k), uri_encode(v)) for k, v in sorted(query.items())),
        ''.join('%s:%s\n' % (n, lowered[n]) for n in names),
        signed,
        payload_hash,
    ])
    return canonical, signed


def _hmac(key, text):
    return hmac.new(key, text.encode(), hashlib.sha256).digest()


def signature(secret, amz_date, region, service, canonical):
    day = amz_date[:8]
    scope = '%s/%s/%s/aws4_request' % (day, region, service)
    to_sign = '\n'.join(['AWS4-HMAC-SHA256', amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    key = _hmac(_hmac(_hmac(_hmac(('AWS4' + secret).encode(), day), region), service), 'aws4_request')
    return hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()


class BucketError(Exception):
    pass


class Bucket:
    """An S3 bucket by path-style URL (https://host/bucket), signed with SigV4; R2's region is auto."""

    def __init__(self, url, key_id, secret, region='auto', timeout=60):
        self.url = url.rstrip('/')
        self.key_id, self.secret, self.region, self.timeout = key_id, secret, region, timeout

    def request(self, method, key, body=b''):
        parts = urllib.parse.urlsplit(self.url + '/' + key)
        amz_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        payload = hashlib.sha256(body).hexdigest()
        headers = {'Host': parts.netloc, 'x-amz-content-sha256': payload, 'x-amz-date': amz_date}
        canonical, signed = canonical_request(method, urllib.parse.unquote(parts.path), {}, headers, payload)
        headers['Authorization'] = 'AWS4-HMAC-SHA256 Credential=%s/%s/%s/s3/aws4_request, SignedHeaders=%s, Signature=%s' % (
            self.key_id, amz_date[:8], self.region, signed,
            signature(self.secret, amz_date, self.region, 's3', canonical))
        del headers['Host']
        req = urllib.request.Request(urllib.parse.urlunsplit(parts), data=body if method == 'PUT' else None,
                                     method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (OSError, ValueError) as e:
            raise BucketError('%s %s: %s' % (method, key, e))

    def put(self, key, body):
        status, answer = self.request('PUT', key, body)
        if status != 200:
            raise BucketError('PUT %s: %d %s' % (key, status, answer[:200]))

    def get(self, key):
        status, answer = self.request('GET', key)
        if status == 404:
            return None
        if status != 200:
            raise BucketError('GET %s: %d %s' % (key, status, answer[:200]))
        return answer
