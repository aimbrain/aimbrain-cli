import base64
import hashlib
import hmac
import json
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

AIMBRAIN_PROD = 'api.aimbrain.com'
AIMBRAIN_DEV = 'dev.aimbrain.com'
LOCAL = 'localhost:8080'


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

        self.protocol = 'https'
        self.extra_headers = {}
        if options.get('--dev'):
            self.base_url = AIMBRAIN_DEV
        elif options.get('--local'):
            self.protocol = 'http'
            self.base_url = LOCAL
            self.extra_headers['X-Forwarded-For'] = '127.0.0.1'
        else:
            self.base_url = AIMBRAIN_PROD

        # For debug/errors
        self.raw_session = None

        self.session = self.get_session()

        self.auth_method = 'face' if options.get('face') else 'voice'

    def get_hmac_sig(self, method, endpoint, body):
        message = '%s\n%s\n%s' % (method.upper(), endpoint.lower(), body)

        return base64.b64encode(hmac.new(
            self.secret.encode('utf-8'),
            bytes(message).encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest())

    def get_url(self, endpoint):
        return urlparse.urlunparse((
            self.protocol,
            self.base_url,
            endpoint,
            '',
            '',
            '',
        ))

    def get_session(self):
        payload = json.dumps({
            'userId': self.user_id,
            'device': self.device,
            'system': self.system
        })

        session_url = self.get_url(V1_SESSIONS_ENDPOINT)
        headers = self.get_aimbrain_headers(
            'POST',
            V1_SESSIONS_ENDPOINT,
            payload
        )
        start = time.time()
        resp = requests.post(session_url, payload, headers=headers)
        end = time.time() - start
        self.raw_session = resp.text

        response_payload = ''
        session = ''

        try:
            response_payload = resp.json()
            session = response_payload.get('session')
        except ValueError:
            response_payload = resp.reason

        print('\n[%s][%d][%.2fs] %s\n' % (
            V1_SESSIONS_ENDPOINT,
            resp.status_code,
            end,
            response_payload
        ))
        if not session:
            raise SystemExit('Failed to get session, got: %s' % resp.text)

        return session

    def get_aimbrain_headers(self, method, endpoint, body):
        headers = {
            'X-Aimbrain-Apikey': self.api_key,
            'X-Aimbrain-Signature': self.get_hmac_sig(method, endpoint, body),
        }

        headers.update(self.extra_headers)

        return headers

    def encode_biometric(self, biometric_path):
        encoded = None
        with open(biometric_path, 'rb') as f:
            image = f.read()
            encoded = base64.b64encode(image)

        return encoded

    def do_request(self, endpoint, body):
        body['session'] = self.session
        payload = json.dumps(body)
        headers = self.get_aimbrain_headers('POST', endpoint, payload)
        request_url = self.get_url(endpoint)

        now = time.time()
        resp = requests.post(request_url, payload, headers=headers)
        end = time.time() - now

        response_payload = ''
        try:
            response_payload = resp.json()
        except ValueError:
            response_payload = resp.reason

        return '\n[%s][%d][%.2fs] %s\n' % (
            endpoint,
            resp.status_code,
            end,
            response_payload
        )


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

        else:
            # We should never get here...
            raise SystemExit('Unknown auth method "%s"' % self.auth_method)

        if self.token:
            print(self.do_request(token_endpoint, {'tokentype': self.token}))

        body = {biometric_key: []}
        for biometric in self.biometrics:
            body[biometric_key].append(self.encode_biometric(biometric))

        print(self.do_request(endpoint, body))


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

            print(self.do_request(V1_FACE_COMPARE_ENDPOINT, body))


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

        print(self.do_request(endpoint, body))


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

        print(self.do_request(endpoint, {'tokentype': self.token}))


class Session(AbstractRequestGenerator):
    """
    Implements session requests for both face and voice.
    """

    def run(self):
        pass
