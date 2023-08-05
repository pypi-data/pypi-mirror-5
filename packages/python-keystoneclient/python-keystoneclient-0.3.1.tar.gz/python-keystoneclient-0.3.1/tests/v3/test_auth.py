import copy
import json
import requests

from keystoneclient import exceptions
from keystoneclient.v3 import client

from tests.v3 import utils


class AuthenticateAgainstKeystoneTests(utils.TestCase):
    def setUp(self):
        super(AuthenticateAgainstKeystoneTests, self).setUp()
        self.TEST_RESPONSE_DICT = {
            "token": {
                "methods": [
                    "token",
                    "password"
                ],

                "expires_at": "2020-01-01T00:00:10.000123Z",
                "project": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_TENANT_ID,
                    "name": self.TEST_TENANT_NAME
                },
                "user": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_USER,
                    "name": self.TEST_USER
                },
                "issued_at": "2013-05-29T16:55:21.468960Z",
                "catalog": self.TEST_SERVICE_CATALOG
            },
        }
        self.TEST_REQUEST_BODY = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "domain": {
                                "name": self.TEST_DOMAIN_NAME
                            },
                            "name": self.TEST_USER,
                            "password": self.TEST_TOKEN
                        }
                    }
                },
                "scope": {
                    "project": {
                        "id": self.TEST_TENANT_ID
                    },
                }
            }
        }
        self.TEST_REQUEST_HEADERS = {
            'Content-Type': 'application/json',
            'User-Agent': 'python-keystoneclient'
        }
        self.TEST_RESPONSE_HEADERS = {
            'X-Subject-Token': self.TEST_TOKEN
        }

    def test_authenticate_success(self):
        TEST_TOKEN = "abcdef"
        self.TEST_RESPONSE_HEADERS['X-Subject-Token'] = TEST_TOKEN
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']['user']['domain']
        del ident['password']['user']['name']
        ident['password']['user']['id'] = self.TEST_USER
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(user_id=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           project_id=self.TEST_TENANT_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_token, TEST_TOKEN)

    def test_authenticate_failure(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        ident['password']['user']['password'] = 'bad_key'
        resp = utils.TestResponse({
            "status_code": 401,
            "text": json.dumps({
                "unauthorized": {
                    "message": "Unauthorized",
                    "code": "401",
                },
            }),
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        # Workaround for issue with assertRaises on python2.6
        # where with assertRaises(exceptions.Unauthorized): doesn't work
        # right
        def client_create_wrapper():
            client.Client(user_domain_name=self.TEST_DOMAIN_NAME,
                          username=self.TEST_USER,
                          password="bad_key",
                          project_id=self.TEST_TENANT_ID,
                          auth_url=self.TEST_URL)

        self.assertRaises(exceptions.Unauthorized, client_create_wrapper)

    def test_auth_redirect(self):
        correct_response = json.dumps(self.TEST_RESPONSE_DICT, sort_keys=True)
        dict_responses = [
            {
                "headers": {
                    'location': self.TEST_ADMIN_URL + "/auth/tokens",
                    'X-Subject-Token': self.TEST_TOKEN,
                },
                "status_code": 305,
                "text": "Use proxy",
            },
            {
                "headers": {'X-Subject-Token': self.TEST_TOKEN},
                "status_code": 200,
                "text": correct_response,
            },
        ]
        responses = [(utils.TestResponse(resp))
                     for resp in dict_responses]

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn(responses[0])
        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_ADMIN_URL + "/auth/tokens",
                         **kwargs).AndReturn(responses[1])
        self.mox.ReplayAll()

        cs = client.Client(user_domain_name=self.TEST_DOMAIN_NAME,
                           username=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           project_id=self.TEST_TENANT_ID,
                           auth_url=self.TEST_URL)

        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_domain_username_password_scoped(self):
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(user_domain_name=self.TEST_DOMAIN_NAME,
                           username=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           project_id=self.TEST_TENANT_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_userid_password_domain_scoped(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']['user']['domain']
        del ident['password']['user']['name']
        ident['password']['user']['id'] = self.TEST_USER

        scope = self.TEST_REQUEST_BODY['auth']['scope']
        del scope['project']
        scope['domain'] = {}
        scope['domain']['id'] = self.TEST_DOMAIN_ID

        token = self.TEST_RESPONSE_DICT['token']
        del token['project']
        token['domain'] = {}
        token['domain']['id'] = self.TEST_DOMAIN_ID
        token['domain']['name'] = self.TEST_DOMAIN_NAME

        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS

        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(user_id=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           domain_id=self.TEST_DOMAIN_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_domain_id,
                         self.TEST_DOMAIN_ID)
        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_userid_password_project_scoped(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']['user']['domain']
        del ident['password']['user']['name']
        ident['password']['user']['id'] = self.TEST_USER

        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS

        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(user_id=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           project_id=self.TEST_TENANT_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_tenant_id,
                         self.TEST_TENANT_ID)
        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_password_unscoped(self):
        del self.TEST_RESPONSE_DICT['token']['catalog']
        del self.TEST_REQUEST_BODY['auth']['scope']
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(user_domain_name=self.TEST_DOMAIN_NAME,
                           username=self.TEST_USER,
                           password=self.TEST_TOKEN,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])
        self.assertFalse('catalog' in cs.service_catalog.catalog)

    def test_authenticate_success_token_domain_scoped(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']
        ident['methods'] = ['token']
        ident['token'] = {}
        ident['token']['id'] = self.TEST_TOKEN

        scope = self.TEST_REQUEST_BODY['auth']['scope']
        del scope['project']
        scope['domain'] = {}
        scope['domain']['id'] = self.TEST_DOMAIN_ID

        token = self.TEST_RESPONSE_DICT['token']
        del token['project']
        token['domain'] = {}
        token['domain']['id'] = self.TEST_DOMAIN_ID
        token['domain']['name'] = self.TEST_DOMAIN_NAME

        self.TEST_REQUEST_HEADERS['X-Auth-Token'] = self.TEST_TOKEN
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(token=self.TEST_TOKEN,
                           domain_id=self.TEST_DOMAIN_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_domain_id,
                         self.TEST_DOMAIN_ID)
        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_token_project_scoped(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']
        ident['methods'] = ['token']
        ident['token'] = {}
        ident['token']['id'] = self.TEST_TOKEN
        self.TEST_REQUEST_HEADERS['X-Auth-Token'] = self.TEST_TOKEN
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(token=self.TEST_TOKEN,
                           project_id=self.TEST_TENANT_ID,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_tenant_id,
                         self.TEST_TENANT_ID)
        self.assertEqual(cs.management_url,
                         self.TEST_RESPONSE_DICT["token"]["catalog"][3]
                         ['endpoints'][2]["url"])
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])

    def test_authenticate_success_token_unscoped(self):
        ident = self.TEST_REQUEST_BODY['auth']['identity']
        del ident['password']
        ident['methods'] = ['token']
        ident['token'] = {}
        ident['token']['id'] = self.TEST_TOKEN
        del self.TEST_REQUEST_BODY['auth']['scope']
        del self.TEST_RESPONSE_DICT['token']['catalog']
        self.TEST_REQUEST_HEADERS['X-Auth-Token'] = self.TEST_TOKEN
        resp = utils.TestResponse({
            "status_code": 200,
            "text": json.dumps(self.TEST_RESPONSE_DICT),
            "headers": self.TEST_RESPONSE_HEADERS,
        })

        kwargs = copy.copy(self.TEST_REQUEST_BASE)
        kwargs['headers'] = self.TEST_REQUEST_HEADERS
        kwargs['data'] = json.dumps(self.TEST_REQUEST_BODY, sort_keys=True)
        requests.request('POST',
                         self.TEST_URL + "/auth/tokens",
                         **kwargs).AndReturn((resp))
        self.mox.ReplayAll()

        cs = client.Client(token=self.TEST_TOKEN,
                           auth_url=self.TEST_URL)
        self.assertEqual(cs.auth_token,
                         self.TEST_RESPONSE_HEADERS["X-Subject-Token"])
        self.assertFalse('catalog' in cs.service_catalog.catalog)
