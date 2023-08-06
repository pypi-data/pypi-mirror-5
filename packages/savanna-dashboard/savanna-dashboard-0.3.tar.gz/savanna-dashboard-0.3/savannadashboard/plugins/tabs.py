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

from django.utils.translation import ugettext_lazy as _

import logging

from horizon import tabs
from savannadashboard.api.client import client as savannaclient

LOG = logging.getLogger(__name__)


class DetailsTab(tabs.Tab):
    name = _("Details")
    slug = "plugin_details_tab"
    template_name = ("plugins/_details.html")

    def get_context_data(self, request):
        plugin_id = self.tab_group.kwargs['plugin_id']
        savanna = savannaclient(request)
        plugin = savanna.plugins.get(plugin_id)
        return {"plugin": plugin}


class PluginDetailsTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (DetailsTab,)
    sticky = True
