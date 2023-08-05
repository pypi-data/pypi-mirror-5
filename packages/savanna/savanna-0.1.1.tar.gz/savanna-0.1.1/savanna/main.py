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

from eventlet import monkey_patch
from flask import Flask
from keystoneclient.middleware.auth_token import filter_factory as auth_token
from oslo.config import cfg
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from savanna.api import v02 as api_v02
from savanna.middleware.auth_valid import filter_factory as auth_valid
from savanna.storage.db import setup_storage
from savanna.utils.api import render
from savanna.utils.scheduler import setup_scheduler

from savanna.openstack.common import log

LOG = log.getLogger(__name__)

monkey_patch(os=True, select=True, socket=True, thread=True, time=True)

opts = [
    cfg.StrOpt('os_auth_protocol',
               default='http',
               help='Protocol used to access OpenStack Identity service'),
    cfg.StrOpt('os_auth_host',
               default='openstack',
               help='IP or hostname of machine on which OpenStack Identity '
                    'service is located'),
    cfg.StrOpt('os_auth_port',
               default='35357',
               help='Port of OpenStack Identity service'),
    cfg.StrOpt('os_admin_username',
               default='admin',
               help='This OpenStack user is used to verify provided tokens. '
                    'The user must have admin role in <os_admin_tenant_name> '
                    'tenant'),
    cfg.StrOpt('os_admin_password',
               default='nova',
               help='Password of the admin user'),
    cfg.StrOpt('os_admin_tenant_name',
               default='admin',
               help='Name of tenant where the user is admin')
]

CONF = cfg.CONF
CONF.register_opts(opts)


def make_app():
    """App builder (wsgi)

    Entry point for Savanna REST API server
    """
    app = Flask('savanna.api')

    @app.route('/', methods=['GET'])
    def version_list():
        return render({
            "versions": [
                {"id": "v0.2", "status": "CURRENT"}
            ]
        })

    app.register_blueprint(api_v02.rest, url_prefix='/v0.2')

    setup_storage(app)
    setup_scheduler(app)

    def make_json_error(ex):
        status_code = (ex.code
                       if isinstance(ex, HTTPException)
                       else 500)
        description = (ex.description
                       if isinstance(ex, HTTPException)
                       else str(ex))
        return render({'error': status_code, 'error_message': description},
                      status=status_code)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    app.wsgi_app = auth_valid(app.config)(app.wsgi_app)

    app.wsgi_app = auth_token(
        app.config,
        auth_host=CONF.os_auth_host,
        auth_port=CONF.os_auth_port,
        auth_protocol=CONF.os_auth_protocol,
        admin_user=CONF.os_admin_username,
        admin_password=CONF.os_admin_password,
        admin_tenant=CONF.os_admin_tenant_name
    )(app.wsgi_app)

    return app
