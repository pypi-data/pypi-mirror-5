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

from flask import request
import functools
import jsonschema
from oslo.config import cfg

from savanna import exceptions as ex
import savanna.openstack.common.exception as os_ex
from savanna.openstack.common import log as logging
from savanna.service import api
import savanna.utils.api as api_u
from savanna.utils.openstack import nova


LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.import_opt('allow_cluster_ops', 'savanna.config')

# Base validation schema of cluster creation operation
CLUSTER_CREATE_SCHEMA = {
    "title": "Cluster creation schema",
    "type": "object",
    "properties": {
        "cluster": {
            "type": "object",
            "properties": {
                "name": {"type": "string",
                         "minLength": 1,
                         "maxLength": 50,
                         "pattern": r"^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]"
                                    r"*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z]"
                                    r"[A-Za-z0-9\-]*[A-Za-z0-9])$"},
                "base_image_id": {"type": "string",
                                  "minLength": 1,
                                  "maxLength": 240},
                "node_templates": {
                    "type": "object"
                }
            },
            "required": ["name", "base_image_id", "node_templates"]
        }
    },
    "required": ["cluster"]
}

# Base validation schema of node template creation operation
TEMPLATE_CREATE_SCHEMA = {
    "title": "Node Template creation schema",
    "type": "object",
    "properties": {
        "node_template": {
            "type": "object",
            "properties": {
                "name": {"type": "string",
                         "minLength": 1,
                         "maxLength": 240,
                         "pattern": r"^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-_]"
                                    r"*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z]"
                                    r"[A-Za-z0-9\-_]*[A-Za-z0-9])$"},
                "node_type": {"type": "string",
                              "minLength": 1,
                              "maxLength": 240},
                "flavor_id": {"type": "string",
                              "minLength": 1,
                              "maxLength": 240},
                "task_tracker": {
                    "type": "object"
                },
                "job_tracker": {
                    "type": "object"
                },
                "name_node": {
                    "type": "object"
                },
                "data_node": {
                    "type": "object"
                }
            },
            "required": ["name", "node_type", "flavor_id"]
        }
    },
    "required": ["node_template"]
}


def validate(validate_func):
    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            try:
                validate_func(api_u.request_data(), **kwargs)
            except jsonschema.ValidationError, e:
                e.code = "VALIDATION_ERROR"
                return api_u.bad_request(e)
            except ex.SavannaException, e:
                return api_u.bad_request(e)
            except os_ex.MalformedRequestBody, e:
                e.code = "MALFORMED_REQUEST_BODY"
                return api_u.bad_request(e)
            except Exception, e:
                return api_u.internal_error(
                    500, "Error occurred during validation", e)

            return func(*args, **kwargs)

        return handler

    return decorator


def exists_by_id(service_func, id_prop, tenant_specific=False):
    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            try:
                if tenant_specific:
                    tenant = request.headers['X-Tenant-Id']
                    service_func(*args, id=kwargs[id_prop], tenant_id=tenant)
                else:
                    service_func(*args, id=kwargs[id_prop])
                return func(*args, **kwargs)
            except ex.NotFoundException, e:
                e.__init__(kwargs[id_prop])
                return api_u.not_found(e)
            except Exception, e:
                return api_u.internal_error(
                    500, "Unexpected error occurred", e)

        return handler

    return decorator


def validate_cluster_create(cluster_values):
    jsonschema.validate(cluster_values, CLUSTER_CREATE_SCHEMA)
    values = cluster_values['cluster']

    # check that requested cluster name is unique
    unique_names = [cluster.name for cluster in api.get_clusters()]
    if values['name'] in unique_names:
        raise ex.ClusterNameExistedException(values['name'])

    # check that requested templates are from already defined values
    node_templates = values['node_templates']
    possible_node_templates = [nt.name for nt in api.get_node_templates()]
    for nt in node_templates:
        if nt not in possible_node_templates:
            raise ex.NodeTemplateNotFoundException(nt)
        # check node count is integer and non-zero value
        jsonschema.validate(node_templates[nt],
                            {"type": "integer", "minimum": 1})

    # check that requested cluster contains only 1 instance of NameNode
    # and 1 instance of JobTracker
    jt_count = 0
    nn_count = 0

    for nt_name in node_templates:
        processes = api.get_node_template(name=nt_name).dict['node_type'][
            'processes']
        if "job_tracker" in processes:
            jt_count += node_templates[nt_name]
        if "name_node" in processes:
            nn_count += node_templates[nt_name]

    if nn_count != 1:
        raise ex.NotSingleNameNodeException(nn_count)

    if jt_count != 1:
        raise ex.NotSingleJobTrackerException(jt_count)

    if CONF.allow_cluster_ops:
        image_id = values['base_image_id']
        nova_images = nova.get_images(request.headers)
        if image_id not in nova_images:
            LOG.debug("Could not find %s image in %s", image_id, nova_images)
            raise ex.ImageNotFoundException(values['base_image_id'])

        # check available Nova absolute limits
        _check_limits(nova.get_limits(request.headers),
                      values['node_templates'])
    else:
        LOG.info("Cluster ops are disabled, use --allow-cluster-ops flag")


def validate_node_template_create(nt_values):
    jsonschema.validate(nt_values, TEMPLATE_CREATE_SCHEMA)
    values = nt_values['node_template']

    # check that requested node_template name is unique
    unique_names = [nt.name for nt in api.get_node_templates()]
    if values['name'] in unique_names:
        raise ex.NodeTemplateExistedException(values['name'])

    node_types = [nt.name for nt in api.get_node_types()]

    if values['node_type'] not in node_types:
        raise ex.NodeTypeNotFoundException(values['node_type'])

    req_procs = []
    if "TT" in values['node_type']:
        req_procs.append("task_tracker")
    if "DN" in values['node_type']:
        req_procs.append("data_node")
    if "NN" in values['node_type']:
        req_procs.append("name_node")
    if "JT" in values['node_type']:
        req_procs.append("job_tracker")

    LOG.debug("Required properties are: %s", req_procs)

    jsonschema.validate(values, {"required": req_procs})

    processes = values.copy()
    del processes['name']
    del processes['node_type']
    del processes['flavor_id']

    LOG.debug("Incoming properties are: %s", processes)

    for proc in processes:
        if proc not in req_procs:
            raise ex.DiscrepancyNodeProcessException(req_procs)

    req_params = api.get_node_type_required_params(name=values['node_type'])
    for process in req_params:
        for param in req_params[process]:
            if param not in values[process] or not values[process][param]:
                raise ex.RequiredParamMissedException(process, param)

    all_params = api.get_node_type_all_params(name=values['node_type'])
    for process in all_params:
        for param in processes[process]:
            if param not in all_params[process]:
                raise ex.ParamNotAllowedException(param, process)

    if api.CONF.allow_cluster_ops:
        flavor = values['flavor_id']
        nova_flavors = nova.get_flavors(request.headers)
        if flavor not in nova_flavors:
            LOG.debug("Could not find %s flavor in %s", flavor, nova_flavors)
            raise ex.FlavorNotFoundException(flavor)
    else:
        LOG.info("Cluster ops are disabled, use --allow-cluster-ops flag")


def _check_limits(limits, node_templates):
    all_vcpus = limits['maxTotalCores'] - limits['totalCoresUsed']
    all_ram = limits['maxTotalRAMSize'] - limits['totalRAMUsed']
    all_inst = limits['maxTotalInstances'] - limits['totalInstancesUsed']
    LOG.info("List of available VCPUs: %d, RAM: %d, Instances: %d",
             all_vcpus, all_ram, all_inst)

    need_vcpus = 0
    need_ram = 0
    need_inst = 0
    for nt_name in node_templates:
        nt_flavor_name = api.get_node_template(name=nt_name).dict['flavor_id']
        nt_flavor_count = node_templates[nt_name]
        LOG.debug("User requested flavor: %s, count: %s",
                  nt_flavor_name, nt_flavor_count)
        nova_flavor = nova.get_flavor(request.headers, name=nt_flavor_name)
        LOG.debug("Nova has flavor %s with VCPUs=%d, RAM=%d",
                  nova_flavor.name, nova_flavor.vcpus, nova_flavor.ram)

        need_vcpus += nova_flavor.vcpus * nt_flavor_count
        need_ram += nova_flavor.ram * nt_flavor_count
        need_inst += nt_flavor_count

    LOG.info("User requested %d instances with total VCPUs=%d and RAM=%d",
             need_inst, need_vcpus, need_ram)

    if need_inst > all_inst or need_vcpus > all_vcpus or need_ram > all_ram:
        raise ex.NotEnoughResourcesException([all_inst, all_vcpus, all_ram,
                                              need_inst, need_vcpus, need_ram])


def validate_node_template_terminate(_, template_id):
    if api.is_node_template_associated(id=template_id):
        name = api.get_node_template(id=template_id).name
        raise ex.AssociatedNodeTemplateTerminationException(name)
