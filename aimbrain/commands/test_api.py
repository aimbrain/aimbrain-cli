from tempfile import NamedTemporaryFile

import mock
import unittest2

from mock import MagicMock
from mock import patch

from aimbrain.commands.api import AbstractRequestGenerator
from aimbrain.commands.api import BehaviouralSubmit
from aimbrain.commands.api import V1_BEHAVIOURAL_SUBMIT


class TestBaseAPI(unittest2.TestCase):

    def test_hmac_signature_generation(self):
        options = {
            '--secret': 'bannanaman',
            '--api-url': 'https://api.aimbrain.com'
        }
        self.api = AbstractRequestGenerator(options)

        test_sig = self.api.get_hmac(
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
        options = {'--api-url': 'https://api.aimbrain.com'}
        self.api = AbstractRequestGenerator(options)

        with NamedTemporaryFile('w+b') as f:
            f.write('boop')
            f.seek(0)
            encoding = self.api.encode_biometric(f.name)
            self.assertEquals('Ym9vcA==', encoding)

    def test_biometric_encoding_non_existant_file(self):
        options = {'--api-url': 'https://api.aimbrain.com'}
        self.api = AbstractRequestGenerator(options)

        with self.assertRaises(SystemExit):
            self.api.encode_biometric('ifthisfileexistsyouhaveissuesm8')


class TestBehaviouralSubmit(unittest2.TestCase):
    @patch('os.path.exists', return_value=False)
    def test_run_non_existent(self, exists):
        options = {
            '--api-url': 'https://api.aimbrain.com',
            '--data': '/tmp/test-data.json',
        }
        api = BehaviouralSubmit(options)
        with self.assertRaises(SystemExit):
            api.run()

    @patch('os.path.exists', return_value=True)
    @patch('__builtin__.open')
    @patch('json.load', return_value='test-data')
    def test_run_exists(self, exists, mopen, jl):
        options = {
            '--api-url': 'https://api.aimbrain.com',
            '--data': '/tmp/test-data.json',
        }
        api = BehaviouralSubmit(options)
        api.do_request = MagicMock()
        api.run()
        api.do_request.assert_called_with(V1_BEHAVIOURAL_SUBMIT, 'test-data')
