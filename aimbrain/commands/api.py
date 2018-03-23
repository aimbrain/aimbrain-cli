import base64
import hashlib
import hmac
import json
import os
import time
import urlparse

import requests

from aimbrain.commands.base import BaseCommand

V1_SESSIONS_ENDPOINT = '/v1/sessions'

V1_FACE_AUTH_ENDPOINT = '/v1/face/auth'
V1_FACE_COMPARE_ENDPOINT = '/v1/face/compare'
V1_FACE_ENROLL_ENDPOINT = '/v1/face/enroll'
V1_FACE_TOKEN_ENDPOINT = '/v1/face/token'

V1_VOICE_AUTH_ENDPOINT = '/v1/voice/auth'
V1_VOICE_ENROLL_ENDPOINT = '/v1/voice/enroll'
V1_VOICE_TOKEN_ENDPOINT = '/v1/voice/token'


class AbstractRequestGenerator(BaseCommand):
    """
    Implements all the standard AimBrain functionality such as HMAC
    signatueres, session generation and performs the requests themselves.
    """

    def __init__(self, options, *args, **kwargs):
        super(AbstractRequestGenerator, self).__init__(options, args, kwargs)

        self.user_id = options.get('--user-id')
        self.secret = options.get('--secret')
        self.api_key = options.get('--api-key')

        self.device = options.get('--device')
        self.system = options.get('--system')

        self.extra_headers = {}
        self.base_url = options.get('--api-url', '')
        if 'localhost' in self.base_url:
            self.extra_headers['X-Forwarded-For'] = '127.0.0.1'

        self.auth_method = 'face' if options.get('face') else 'voice'
        self.session = None

    def get_hmac_sig(self, method, endpoint, payload):
        """
        Generate a HMAC signature

        Arguments:
        method <string> -- HTTP method e.g. GET, POST
        endpoint <string> -- HTTP endpoint request is being sent to
        payload <string> -- JSON encoded body of request
        """

        message = '%s\n%s\n%s' % (method.upper(), endpoint.lower(), payload)

        return base64.b64encode(hmac.new(
            self.secret.encode('utf-8'),
            bytes(message).encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest())

    def get_aimbrain_headers(self, method, endpoint, payload):
        """
        Get headers needed for AimBrain API request and any additional ones

        Arguments:
        method <string> -- HTTP method e.g. GET, POST
        endpoint <string> -- HTTP endpoint request is being sent to
        payload <string> -- JSON encoded body of request
        """

        headers = {
            'X-Aimbrain-Apikey': self.api_key,
            'X-Aimbrain-Signature': self.get_hmac_sig(method, endpoint, payload),
        }

        headers.update(self.extra_headers)

        return headers

    def get_url(self, endpoint):
        """
        Generate a full URL for a particular endpoint

        Arguments:
        endpoint <string> -- HTTP endpoint request is being sent to
        """

        url_params = urlparse.urlparse(self.base_url)
        if not url_params[0]:
            raise SystemExit('--api-url requires a scheme e.g. http')

        return urlparse.urlunparse((
            url_params[0],
            url_params[1],
            endpoint,
            '',
            '',
            '',
        ))

    def post(self, url, payload, headers):
        """
        POST a request to a URL

        Arguments:
        url <string> -- HTTP method e.g. GET, POST
        endpoint <string> -- HTTP endpoint request is being sent to
        headers <dict> -- Dictionary of header keys to values
        """

        start = time.time()
        resp = None
        try:
            resp = requests.post(url, payload, headers=headers)
        except requests.exceptions.ConnectionError:
            raise SystemExit('Unable to connect to url "%s"' % url)

        end = time.time() - start

        return resp, end

    def get_response_payload(self, endpoint, payload):
        """
        Send a request to AimBrain API and return JSON response

        Arguments:
        endpoint <string> -- HTTP endpoint request is being sent to
        payload <string> -- JSON encoded body of request
        """

        url = self.get_url(endpoint)
        headers = self.get_aimbrain_headers(
            'POST',
            endpoint,
            payload
        )

        resp, end = self.post(url, payload, headers)

        response_payload = ''
        try:
            response_payload = resp.json()
        except ValueError:
            pass

        print('\n[%s][%d][%.2fs] %s\n' % (
            endpoint,
            resp.status_code,
            end,
            response_payload or resp.text
        ))

        if not response_payload:
            raise SystemExit('Failed to get session, got: %s' % resp.text)

        return response_payload

    def get_session(self):
        """
        Get session for this request batch
        """

        if self.session:
            return self.session

        payload = json.dumps({
            'userId': self.user_id,
            'device': self.device,
            'system': self.system
        })

        response_payload = self.get_response_payload(
            V1_SESSIONS_ENDPOINT,
            payload
        )

        self.session = response_payload.get('session')
        if not self.session:
            raise SystemExit('Failed to get session')

        return self.session

    def encode_biometric(self, biometric_path):
        """
        Encode the biometric asset (image, video, audio) to base64

        Arguments:
        biometric_path <string> -- file path to asset 
        """
        if not os.path.exists(biometric_path):
            raise SystemExit('"%s" path does not exist' % biometric_path)

        encoded = None
        with open(biometric_path, 'rb') as f:
            image = f.read()
            encoded = base64.b64encode(image)

        return encoded

    def do_request(self, endpoint, body, require_session=True):
        """
        Send a request to AimBrain API

        Arguments:
        endpoint <string> -- HTTP endpoint request is being sent to
        body <dict> -- Body of request
        """

        if require_session:
            body['session'] = self.get_session()

        self.get_response_payload(endpoint, json.dumps(body))


class Auth(AbstractRequestGenerator):
    """
    Implements authentication requests for both face and voice.
    """

    def __init__(self, options, *args, **kwargs):
        super(Auth, self).__init__(options, args, kwargs)

        self.token = options.get('--token')
        self.biometrics = options.get('<biometrics>')

    def run(self):
        token_endpoint = ''
        endpoint = ''
        biometric_key = ''

        if self.auth_method == 'face':
            token_endpoint = V1_FACE_TOKEN_ENDPOINT
            endpoint = V1_FACE_AUTH_ENDPOINT
            biometric_key = 'faces'

        elif self.auth_method == 'voice':
            token_endpoint = V1_VOICE_TOKEN_ENDPOINT
            endpoint = V1_VOICE_AUTH_ENDPOINT
            biometric_key = 'voices'

            # Voice requires token
            if not self.token:
                raise SystemExit('A token is required for voice auth')

        else:
            # We should never get here...
            raise SystemExit('Unknown auth method "%s"' % self.auth_method)

        if self.token:
            self.do_request(token_endpoint, {'tokentype': self.token})

        body = {biometric_key: []}
        for biometric in self.biometrics:
            body[biometric_key].append(self.encode_biometric(biometric))

        self.do_request(endpoint, body)


class Compare(AbstractRequestGenerator):
    """
    Implements authentication requests for face.
    """

    def __init__(self, options, *args, **kwargs):
        super(Compare, self).__init__(options, args, kwargs)

        self.biometric1 = options.get('<biometric1>')
        self.biometric2 = options.get('<biometric2>')

    def run(self):
        if self.auth_method == 'face':
            body = {
                'faces1': [self.encode_biometric(self.biometric1)],
                'faces2': [self.encode_biometric(self.biometric2)]
            }

            self.do_request(
                V1_FACE_COMPARE_ENDPOINT,
                body,
                require_session=False,
            )


class Enroll(AbstractRequestGenerator):
    """
    Implements enrollment requests for both face and voice.
    """

    def __init__(self, options, *args, **kwargs):
        super(Enroll, self).__init__(options, args, kwargs)

        self.biometrics = options.get('<biometrics>')

    def run(self):
        endpoint = ''
        biometric_key = ''

        if self.auth_method == 'face':
            endpoint = V1_FACE_ENROLL_ENDPOINT
            biometric_key = 'faces'

        elif self.auth_method == 'voice':
            endpoint = V1_VOICE_ENROLL_ENDPOINT
            biometric_key = 'voices'

        else:
            # We should never get here...
            raise SystemExit('Unknown auth method "%s"' % self.auth_method)

        body = {biometric_key: []}
        for biometric in self.biometrics:
            body[biometric_key].append(self.encode_biometric(biometric))

        self.do_request(endpoint, body)


class Token(AbstractRequestGenerator):
    """
    Implements token requests for both face and voice.
    """

    def __init__(self, options, *args, **kwargs):
        super(Token, self).__init__(options, args, kwargs)

        self.token = options.get('--token')

    def run(self):
        endpoint = ''
        if self.auth_method == 'face':
            endpoint = V1_FACE_TOKEN_ENDPOINT
        elif self.auth_method == 'voice':
            endpoint = V1_VOICE_TOKEN_ENDPOINT

        self.do_request(endpoint, {'tokentype': self.token})


class Session(AbstractRequestGenerator):
    """
    Implements session requests for both face and voice.
    """

    def run(self):
        pass
