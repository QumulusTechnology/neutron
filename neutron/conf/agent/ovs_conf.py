# Copyright 2011 VMware, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg

from neutron._i18n import _

# Default timeout for OVSDB commands
DEFAULT_OVSDB_TIMEOUT = 10

OPTS = [
    cfg.IntOpt('ovsdb_timeout',
               default=DEFAULT_OVSDB_TIMEOUT,
               help=_('Timeout in seconds for OVSDB commands. '
                      'If the timeout expires, OVSDB commands will fail with '
                      'ALARMCLOCK error.')),
    cfg.IntOpt('bridge_mac_table_size',
               default=50000,
               help=_('The maximum number of MAC addresses to learn on '
                      'a bridge managed by the Neutron OVS agent. Values '
                      'outside a reasonable range (10 to 1,000,000) might be '
                      'overridden by Open vSwitch according to the '
                      'documentation.')),
    cfg.BoolOpt('igmp_snooping_enable', default=False,
                help=_('Enable IGMP snooping for integration bridge. If this '
                       'option is set to True, support for Internet Group '
                       'Management Protocol (IGMP) is enabled in integration '
                       'bridge. '
                       'Setting this option to True will also enable the Open '
                       'vSwitch mcast-snooping-disable-flood-unregistered '
                       'flag. This option will disable flooding of '
                       'unregistered multicast packets to all ports. '
                       'The switch will send unregistered multicast packets '
                       'only to ports connected to multicast routers.')),
]


def register_ovs_agent_opts(cfg=cfg.CONF):
    cfg.register_opts(OPTS, 'OVS')
