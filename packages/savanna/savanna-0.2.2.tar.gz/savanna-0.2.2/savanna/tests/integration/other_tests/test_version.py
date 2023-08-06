# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import telnetlib

from savanna.tests.integration import base


class RestApiVersionsTest(base.ITestCase):

    def setUp(self):
        super(RestApiVersionsTest, self).setUp()
        telnetlib.Telnet(self.host, self.port)

    def test_version(self):
        """This test checks Savanna version
        """
        version_data = self.get_object(self.url_version, '', 200)
        get_version_data = {'versions': [{'status': 'CURRENT', 'id': 'v1.0'}]}
        self.assertEqual(version_data, get_version_data)
