from tempfile import NamedTemporaryFile

import mock
import unittest2

from mock import MagicMock

from aimbrain.commands.api import AbstractRequestGenerator


class TestBaseAPI(unittest2.TestCase):

    def test_hmac_signature_generation(self):
        options = {'--secret': 'bannanaman'}
        self.api = AbstractRequestGenerator(options)

        test_sig = self.api.get_hmac_sig(
            'POST',
            '/potato',
            '{"hello": "Mr Blobby"}',
        )

        expected_sig = 'LtlMaa6CGTMsY5OTqB8fYZGTJTAaQMLjsYBd0eUJrkk='
        self.assertEquals(test_sig, expected_sig)

    def test_get_url(self):
        options = {'--api-url': 'https://api.aimbrain.com'}
        self.api = AbstractRequestGenerator(options)
        url = self.api.get_url('/blob')
        self.assertEquals(url, 'https://api.aimbrain.com/blob')

    def test_get_url_local(self):
        options = {'--api-url': 'http://localhost:8080'}
        self.api = AbstractRequestGenerator(options)
        url = self.api.get_url('/blob')
        self.assertEquals(url, 'http://localhost:8080/blob')

    def test_get_url_schemeless(self):
        options = {'--api-url': 'localhost:8080'}
        self.api = AbstractRequestGenerator(options)
        with self.assertRaises(SystemExit):
            self.api.get_url('/blob')

    def test_get_session(self):
        options = {
            '--user-id': 'potato',
            '--device': 'golden potato',
            '--system': 'potato-os',
            '--api-url': 'https://api.aimbrain.com',
            '--secret': 'bannanaman',
        }

        self.api = AbstractRequestGenerator(options)
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={'session': 'orange'})
        self.api.post = MagicMock(return_value=(mock_response, 1))
        test_session = self.api.get_session()
        self.assertEquals(test_session, 'orange')

    def test_get_session_failure(self):
        options = {
            '--user-id': 'potato',
            '--device': 'golden potato',
            '--system': 'potato-os',
            '--api-url': 'https://api.aimbrain.com',
            '--secret': 'bannanaman',
        }

        self.api = AbstractRequestGenerator(options)
        mock_response = MagicMock()
        mock_response.json = MagicMock(side_effect=ValueError)
        self.api.post = MagicMock(return_value=(mock_response, 1))
        with self.assertRaises(SystemExit):
            test_session = self.api.get_session()

    def test_biometric_encoding(self):
        self.api = AbstractRequestGenerator({})

        with NamedTemporaryFile('w+b') as f:
            f.write('boop')
            f.seek(0)
            encoding = self.api.encode_biometric(f.name)
            self.assertEquals('Ym9vcA==', encoding)

    def test_biometric_encoding_non_existant_file(self):
        self.api = AbstractRequestGenerator({})

        with self.assertRaises(SystemExit):
            self.api.encode_biometric('ifthisfileexistsyouhaveissuesmate')
