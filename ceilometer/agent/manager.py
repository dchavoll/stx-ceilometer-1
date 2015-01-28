#
# Copyright 2012-2013 eNovance <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystoneclient.v2_0 import client as ksclient
from oslo_config import cfg

from ceilometer.agent import base
from ceilometer.openstack.common import log

OPTS = [
    cfg.StrOpt('partitioning_group_prefix',
               default=None,
               deprecated_group='central',
               help='Work-load partitioning group prefix. Use only if you '
                    'want to run multiple polling agents with different '
                    'config files. For each sub-group of the agent '
                    'pool with the same partitioning_group_prefix a disjoint '
                    'subset of pollsters should be loaded.'),
]

cfg.CONF.register_opts(OPTS, group='polling')
cfg.CONF.import_group('service_credentials', 'ceilometer.service')
cfg.CONF.import_opt('http_timeout', 'ceilometer.service')

LOG = log.getLogger(__name__)


class AgentManager(base.AgentManager):

    def __init__(self, namespaces=None, pollster_list=None):
        namespaces = namespaces or ['compute', 'central']
        pollster_list = pollster_list or []
        super(AgentManager, self).__init__(
            namespaces, pollster_list,
            group_prefix=cfg.CONF.polling.partitioning_group_prefix)

    def interval_task(self, task):
        try:
            self.keystone = ksclient.Client(
                username=cfg.CONF.service_credentials.os_username,
                password=cfg.CONF.service_credentials.os_password,
                tenant_id=cfg.CONF.service_credentials.os_tenant_id,
                tenant_name=cfg.CONF.service_credentials.os_tenant_name,
                cacert=cfg.CONF.service_credentials.os_cacert,
                auth_url=cfg.CONF.service_credentials.os_auth_url,
                region_name=cfg.CONF.service_credentials.os_region_name,
                insecure=cfg.CONF.service_credentials.insecure,
                timeout=cfg.CONF.http_timeout,)
        except Exception as e:
            self.keystone = e

        super(AgentManager, self).interval_task(task)
