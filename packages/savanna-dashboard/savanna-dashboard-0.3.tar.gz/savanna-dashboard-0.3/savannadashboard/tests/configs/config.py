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

import os
from oslo.config import cfg

common_group = cfg.OptGroup(name='common', title="common configs")

CommonGroup = [
    cfg.StrOpt('base_url',
               default='http://127.0.0.1:8080',
               help="savanna url"),
    cfg.StrOpt('user',
               default='admin',
               help="keystone user"),
    cfg.StrOpt('password',
               default='pass',
               help="password for keystone user"),
    cfg.IntOpt('cluster_creation_timeout',
               default=10,
               help="cluster timeout in minutes"),
    cfg.IntOpt('await_element',
               default=10,
               help="await each web element in seconds"),
    cfg.StrOpt('image_name_for_register',
               default='fedora_19',
               help='Image name for register to Savanna'),
    cfg.StrOpt('image_name_for_edit',
               default='latest-ci-image',
               help='Image name for edit in image registry in Savanna')
]

vanilla_group = cfg.OptGroup(name='vanilla', title="vanilla configs")

VanillaGroup = [
    cfg.BoolOpt('skip_plugin_tests',
                default=False,
                help="""
                If this variable is True then
                tests for vanilla will be skipped
                """),
    cfg.StrOpt('plugin_name',
               default='Vanilla Apache Hadoop',
               help="plugin title, default: Vanilla Apache Hadoop"),
    cfg.StrOpt('plugin_overview_name',
               default='vanilla',
               help="plugin name in overview"),
    cfg.StrOpt('hadoop_version',
               default='1.2.1',
               help="hadoop version for plugin"),
    cfg.ListOpt('processes',
                default={"NN": 0, "DN": 1, "SNN": 2,
                         "OZ": 3, "TT": 4, "JT": 5},
                help='numbers of processes for vanilla in savannabashboard'),
    cfg.StrOpt('base_image',
               default='latest-ci-image',
               help="image name for start vanilla cluster")
]

hdp_group = cfg.OptGroup(name='hdp', title="hdp configs")

HdpGroup = [
    cfg.BoolOpt('skip_plugin_tests',
                default=False,
                help="""
                If this variable is True then
                tests for hdp will be skipped
                """),
    cfg.StrOpt('plugin_name',
               default='Hortonworks Data Platform',
               help="plugin title, default: Hortonworks Data Platform"),
    cfg.StrOpt('plugin_overview_name',
               default='hdp',
               help="plugin name in overview"),
    cfg.StrOpt('hadoop_version',
               default='1.3.0',
               help="hadoop version for plugin"),
    cfg.ListOpt('processes',
                default=
                {"NN": 0, "DN": 1, "SNN": 2, "HDFS_CLIENT": 3,
                 "GANGLIA_SERVER": 4, "GANGLIA_MONITOR": 5, "AMBARI_SERVER": 6,
                 "AMBARI_AGENT": 7, "JT": 8, "TT": 9, "MAPREDUCE_CLIENT": 10,
                 "NAGIOS_SERVER": 11},
                help='numbers of processes for hdp in savannabashboard'),
    cfg.StrOpt('base_image',
               default='latest-ci-image',
               help="image name for start hdp cluster")
]


def register_config(config, config_group, config_opts):

    config.register_group(config_group)
    config.register_opts(config_opts, config_group)

path = os.path.join("%s/tests/configs/config.conf" % os.getcwd())

if os.path.exists(path):
    cfg.CONF([], project='savannadashboard', default_config_files=[path])

register_config(cfg.CONF, common_group, CommonGroup)
register_config(cfg.CONF, vanilla_group, VanillaGroup)
register_config(cfg.CONF, hdp_group, HdpGroup)

common = cfg.CONF.common
vanilla = cfg.CONF.vanilla
hdp = cfg.CONF.hdp
