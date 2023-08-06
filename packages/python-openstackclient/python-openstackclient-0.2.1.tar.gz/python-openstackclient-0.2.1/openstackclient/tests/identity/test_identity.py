#   Copyright 2013 OpenStack, LLC.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstackclient.common import clientmanager
from openstackclient.identity import client as identity_client
from openstackclient.tests import utils


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.auth_token = AUTH_TOKEN
        self.auth_url = AUTH_URL


class TestIdentity(utils.TestCase):
    def setUp(self):
        super(TestIdentity, self).setUp()

        api_version = {"identity": "2.0"}

        identity_client.API_VERSIONS = {
            "2.0": "openstackclient.tests.identity.test_identity.FakeClient"
        }

        self.cm = clientmanager.ClientManager(token=AUTH_TOKEN,
                                              url=AUTH_URL,
                                              auth_url=AUTH_URL,
                                              api_version=api_version)

    def test_make_client(self):
        self.assertEqual(self.cm.identity.auth_token, AUTH_TOKEN)
        self.assertEqual(self.cm.identity.auth_url, AUTH_URL)
