# Copyright (c) 2013 Hortonworks, Inc.
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

import mock
import pkg_resources as pkg
import unittest2

from savanna.conductor import resource as r
from savanna.plugins.hdp import ambariplugin as ap
from savanna.plugins.hdp import clusterspec as cs
from savanna.plugins.hdp import exceptions as ex
from savanna import version


GET_REST_REQ = "savanna.plugins.hdp.versions.1_3_2.versionhandler." \
               "AmbariClient._get_rest_request"


def create_cluster_template(ctx, dct):
    return r.ClusterTemplateResource(dct)


class AmbariPluginTest(unittest2.TestCase):
    def test_get_node_processes(self):
        plugin = ap.AmbariPlugin()
        #TODO(jspeidel): provide meaningful input
        service_components = plugin.get_node_processes('1.3.2')

        self.assertEqual(5, len(service_components))
        components = service_components['HDFS']
        self.assertIn('NAMENODE', components)
        self.assertIn('DATANODE', components)
        self.assertIn('SECONDARY_NAMENODE', components)
        self.assertIn('HDFS_CLIENT', components)

        components = service_components['MAPREDUCE']
        self.assertIn('JOBTRACKER', components)
        self.assertIn('TASKTRACKER', components)
        self.assertIn('MAPREDUCE_CLIENT', components)

        components = service_components['GANGLIA']
        self.assertIn('GANGLIA_SERVER', components)
        self.assertIn('GANGLIA_MONITOR', components)

        components = service_components['NAGIOS']
        self.assertIn('NAGIOS_SERVER', components)

        components = service_components['AMBARI']
        self.assertIn('AMBARI_SERVER', components)
        self.assertIn('AMBARI_AGENT', components)

    @mock.patch("savanna.context.ctx")
    def test_convert(self, ctx_func):
        plugin = ap.AmbariPlugin()
        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster = plugin.convert(cluster_config_file, 'ambari', '1.3.2',
                                 'test-plugin', create_cluster_template)
        normalized_config = cs.ClusterSpec(cluster_config_file).normalize()

        self.assertEqual(normalized_config.hadoop_version,
                         cluster.hadoop_version)
        self.assertEqual(len(normalized_config.node_groups),
                         len(cluster.node_groups))

    @mock.patch(GET_REST_REQ)
    def test__set_ambari_credentials__admin_only(self, client):
        client.side_effect = self._get_test_request
        self.requests = []
        plugin = ap.AmbariPlugin()

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster_spec = cs.ClusterSpec(cluster_config_file)

        ambari_info = ap.AmbariInfo(TestHost('111.11.1111'),
                                    '8080', 'admin', 'old-pwd')
        plugin._set_ambari_credentials(cluster_spec, ambari_info, '1.3.2')

        self.assertEqual(1, len(self.requests))
        request = self.requests[0]
        self.assertEqual('put', request.method)
        self.assertEqual('http://111.11.1111:8080/api/v1/users/admin',
                         request.url)
        self.assertEqual('{"Users":{"roles":"admin,user","password":"admin",'
                         '"old_password":"old-pwd"} }', request.data)
        self.assertEqual(('admin', 'old-pwd'), request.auth)
        self.assertEqual('admin', ambari_info.user)
        self.assertEqual('admin', ambari_info.password)

    @mock.patch(GET_REST_REQ)
    def test__set_ambari_credentials__new_user_no_admin(self, client):
        self.requests = []
        plugin = ap.AmbariPlugin()
        client.side_effect = self._get_test_request

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster_spec = cs.ClusterSpec(cluster_config_file)

        for service in cluster_spec.services:
            if service.name == 'AMBARI':
                user = service.users[0]
                user.name = 'test'
                user.password = 'test_pw'

        ambari_info = ap.AmbariInfo(TestHost('111.11.1111'), '8080',
                                    'admin', 'old-pwd')
        plugin._set_ambari_credentials(cluster_spec, ambari_info, '1.3.2')
        self.assertEqual(2, len(self.requests))

        request = self.requests[0]
        self.assertEqual('post', request.method)
        self.assertEqual('http://111.11.1111:8080/api/v1/users/test',
                         request.url)
        self.assertEqual('{"Users":{"password":"test_pw","roles":"admin,user"'
                         '} }', request.data)
        self.assertEqual(('admin', 'old-pwd'), request.auth)

        request = self.requests[1]
        self.assertEqual('delete', request.method)
        self.assertEqual('http://111.11.1111:8080/api/v1/users/admin',
                         request.url)
        self.assertEqual(None, request.data)
        self.assertEqual(('test', 'test_pw'), request.auth)
        self.assertEqual('test', ambari_info.user)
        self.assertEqual('test_pw', ambari_info.password)

    @mock.patch(GET_REST_REQ)
    def test__set_ambari_credentials__new_user_with_admin(self, client):
        self.requests = []
        plugin = ap.AmbariPlugin()
        client.side_effect = self._get_test_request

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster_spec = cs.ClusterSpec(cluster_config_file)

        for service in cluster_spec.services:
            if service.name == 'AMBARI':
                new_user = cs.User('test', 'test_pw', ['user'])
                service.users.append(new_user)

        ambari_info = ap.AmbariInfo(TestHost('111.11.1111'), '8080',
                                    'admin', 'old-pwd')
        plugin._set_ambari_credentials(cluster_spec, ambari_info, '1.3.2')
        self.assertEqual(2, len(self.requests))

        request = self.requests[0]
        self.assertEqual('put', request.method)
        self.assertEqual('http://111.11.1111:8080/api/v1/users/admin',
                         request.url)
        self.assertEqual('{"Users":{"roles":"admin,user","password":"admin",'
                         '"old_password":"old-pwd"} }', request.data)
        self.assertEqual(('admin', 'old-pwd'), request.auth)

        request = self.requests[1]
        self.assertEqual('post', request.method)
        self.assertEqual('http://111.11.1111:8080/api/v1/users/test',
                         request.url)
        self.assertEqual('{"Users":{"password":"test_pw","roles":"user"} }',
                         request.data)
        self.assertEqual(('admin', 'admin'), request.auth)

        self.assertEqual('admin', ambari_info.user)
        self.assertEqual('admin', ambari_info.password)

    @mock.patch(GET_REST_REQ)
    def test__set_ambari_credentials__no_admin_user(self, client):
        self.requests = []
        plugin = ap.AmbariPlugin()
        client.side_effect = self._get_test_request

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster_spec = cs.ClusterSpec(cluster_config_file)

        for service in cluster_spec.services:
            if service.name == 'AMBARI':
                user = service.users[0]
                user.name = 'test'
                user.password = 'test_pw'
                user.groups = ['user']

        ambari_info = ap.AmbariInfo(TestHost('111.11.1111'),
                                    '8080', 'admin', 'old-pwd')
        self.assertRaises(ex.HadoopProvisionError,
                          plugin._set_ambari_credentials(cluster_spec,
                                                         ambari_info, '1.3.2'))

    @mock.patch("savanna.utils.openstack.nova.get_instance_info")
    def test__get_ambari_info(self, patched):
        patched.side_effect = test_get_instance_info

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')

        test_host = TestServer(
            'host1', 'test-master', '111.11.1111',
            '222.11.1111', node_processes=["AMBARI_SERVER"])

        node_group = TestNodeGroup([test_host])
        cluster = TestCluster([node_group])
        cluster_config = cs.ClusterSpec(cluster_config_file, cluster=cluster)
        plugin = ap.AmbariPlugin()

        #change port
        cluster_config.configurations['ambari']['server.port'] = '9000'

        ambari_info = plugin.get_ambari_info(cluster_config)
        self.assertEqual('9000', ambari_info.port)

        #remove port
        del cluster_config.configurations['ambari']['server.port']
        ambari_info = plugin.get_ambari_info(cluster_config)

        self.assertEqual('8080', ambari_info.port)

    def test_update_ambari_info_credentials(self):
        plugin = ap.AmbariPlugin()

        cluster_config_file = pkg.resource_string(
            version.version_info.package,
            'plugins/hdp/versions/1_3_2/resources/default-cluster.template')
        cluster_spec = cs.ClusterSpec(cluster_config_file)

        ambari_info = ap.AmbariInfo(TestHost('111.11.1111'),
                                    '8080', 'admin', 'old-pwd')
        plugin._update_ambari_info_credentials(cluster_spec, ambari_info)

        self.assertEqual('admin', ambari_info.user)
        self.assertEqual('admin', ambari_info.password)

    def _get_test_request(self):
        request = TestRequest()
        self.requests.append(request)
        return request


def test_get_instance_info(*args, **kwargs):
    return TestNova("test_img", "test_flavor")


class TestNova():
    def __init__(self, image, flavor):
        self.image = image
        self.flavor = flavor


class TestCluster:
    def __init__(self, node_groups):
        self.hadoop_version = None
        self.cluster_configs = {}
        self.node_groups = node_groups
        self.default_image_id = '11111'


class TestNodeGroup:
    def __init__(self, instances):
        self.instances = instances


class TestRequest:
    def put(self, url, data=None, auth=None):
        self.url = url
        self.data = data
        self.auth = auth
        self.method = 'put'

        return TestResult(200)

    def post(self, url, data=None, auth=None):
        self.url = url
        self.data = data
        self.auth = auth
        self.method = 'post'

        return TestResult(201)

    def delete(self, url, auth=None):
        self.url = url
        self.auth = auth
        self.data = None
        self.method = 'delete'

        return TestResult(200)


class TestResult:
    def __init__(self, status):
        self.status_code = status
        self.text = ''


class TestServer:
    def __init__(self, hostname, role, public_ip, private_ip,
                 node_processes=None):
        self.hostname = hostname
        self.fqdn = hostname
        self.role = role
        self.management_ip = public_ip
        self.public_ip = public_ip
        self.internal_ip = private_ip
        self.node_processes = node_processes


class TestHost:
    def __init__(self, management_ip, role=None):
        self.management_ip = management_ip
        self.role = role
