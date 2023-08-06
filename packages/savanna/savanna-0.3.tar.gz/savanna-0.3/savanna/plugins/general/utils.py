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


def get_node_groups(cluster, proc_list=list()):
    proc_list = [proc_list] if type(proc_list) in [str, unicode] else proc_list
    return [ng for ng in cluster.node_groups
            if set(proc_list).issubset(ng.node_processes)]


def get_instances(cluster, proc_list=list()):
    nodes = get_node_groups(cluster, proc_list)
    return reduce(lambda a, b: a + b.instances, nodes, [])


def get_instance(cluster, node_process):
    instances = get_instances(cluster, node_process)
    return instances[0] if instances else None


def get_namenode(cluster):
    return get_instance(cluster, "namenode")


def get_jobtracker(cluster):
    return get_instance(cluster, "jobtracker")


def get_oozie(cluster):
    return get_instance(cluster, "oozie")


def get_hiveserver(cluster):
    return get_instance(cluster, "hiveserver")


def get_datanodes(cluster):
    return get_instances(cluster, 'datanode')


def get_tasktrackers(cluster):
    return get_instances(cluster, 'tasktracker')


def get_secondarynamenodes(cluster):
    return get_instances(cluster, 'secondarynamenode')


def generate_host_names(nodes):
    return "\n".join([n.hostname for n in nodes])


def generate_fqdn_host_names(nodes):
    return "\n".join([n.fqdn for n in nodes])
