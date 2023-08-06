#!/usr/bin/env python

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

import gettext
import os
import sys

import eventlet
from eventlet import wsgi

from oslo.config import cfg


# If ../savanna/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
if os.path.exists(os.path.join(possible_topdir,
                               'savanna',
                               '__init__.py')):
    sys.path.insert(0, possible_topdir)

gettext.install('savanna', unicode=1)

from savanna import config
from savanna.db import api as db_api
import savanna.main as server
from savanna.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def main():
    dev_conf = os.path.join(possible_topdir,
                            'etc',
                            'savanna',
                            'savanna.conf')
    config_files = None
    if os.path.exists(dev_conf):
        config_files = [dev_conf]

    config.parse_configs(sys.argv[1:], config_files)
    logging.setup("savanna")

    if not db_api.setup_db():
        raise RuntimeError('Failed to create database!')

    app = server.make_app()

    wsgi.server(eventlet.listen((cfg.CONF.host, cfg.CONF.port), backlog=500),
                app)
