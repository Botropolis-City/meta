import unittest

from s3 import canonical_request, signature

EXAMPLE = {
    'key_id': 'AKIAIOSFODNN7EXAMPLE',
    'secret': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'amz_date': '20130524T000000Z',
    'region': 'us-east-1',
}


class WhenSigningAWSsPublishedPresignedGetExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        query = {'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
                 'X-Amz-Credential': '%s/20130524/us-east-1/s3/aws4_request' % EXAMPLE['key_id'],
                 'X-Amz-Date': EXAMPLE['amz_date'], 'X-Amz-Expires': '86400', 'X-Amz-SignedHeaders': 'host'}
        canonical, _ = canonical_request('GET', '/test.txt', query, {'Host': 'examplebucket.s3.amazonaws.com'},
                                         'UNSIGNED-PAYLOAD')
        cls.signed = signature(EXAMPLE['secret'], EXAMPLE['amz_date'], EXAMPLE['region'], 's3', canonical)

    def test_it_should_match_the_signature_aws_publishes(self):
        self.assertEqual(self.signed, 'aeeed9bbccd4d02ee5c0109b86d86835f995330da4c265957d157751f604d404')


if __name__ == '__main__':
    unittest.main()
