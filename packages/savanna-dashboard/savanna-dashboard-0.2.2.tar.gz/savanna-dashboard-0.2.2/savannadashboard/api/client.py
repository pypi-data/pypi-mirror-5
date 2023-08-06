# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import logging

from savannadashboard.api import cluster_templates
from savannadashboard.api import clusters
from savannadashboard.api import httpclient
from savannadashboard.api import images
from savannadashboard.api import node_group_templates
from savannadashboard.api import plugins
from savannadashboard.utils import importutils

# horizon.api is for backward compatibility with folsom
base = importutils.import_any('openstack_dashboard.api.base',
                              'horizon.api.base')


LOG = logging.getLogger(__name__)


def get_horizon_parameter(name, default_value):
    import openstack_dashboard.settings

    if hasattr(openstack_dashboard.settings, name):
        return getattr(openstack_dashboard.settings, name)
    else:
        logging.info('Parameter %s is not found in local_settings.py, '
                     'using default "%s"' % (name, default_value))
        return default_value


# Both parameters should be defined in Horizon's local_settings.py
# Example SAVANNA_URL - http://localhost:9000/v1.0
SAVANNA_URL = get_horizon_parameter('SAVANNA_URL', None)
# "type" of Savanna service registered in keystone
SAVANNA_SERVICE = get_horizon_parameter('SAVANNA_SERVICE', 'mapreduce')


def get_savanna_url(request):
    if SAVANNA_URL is not None:
        return SAVANNA_URL + '/' + request.user.tenant_id

    return base.url_for(request, SAVANNA_SERVICE)


class Client(object):
    def __init__(self, request):
        self.client = httpclient.HTTPClient(get_savanna_url(request),
                                            request.user.token.id)

        self.clusters = clusters.ClusterManager(self)
        self.cluster_templates = cluster_templates.ClusterTemplateManager(self)
        self.node_group_templates = (node_group_templates.
                                     NodeGroupTemplateManager(self))
        self.plugins = plugins.PluginManager(self)
        self.images = images.ImageManager(self)
