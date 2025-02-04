# Copyright (c) 2021 Red Hat Inc.
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

from unittest import mock

from oslo_policy import policy as base_policy
from oslo_utils import uuidutils

from neutron import policy
from neutron.tests.unit.conf.policies import test_base as base


class SecurityGroupAPITestCase(base.PolicyBaseTestCase):

    def setUp(self):
        super(SecurityGroupAPITestCase, self).setUp()
        self.target = {'project_id': self.project_id}
        self.alt_target = {'project_id': self.alt_project_id}


class SystemAdminSecurityGroupTests(SecurityGroupAPITestCase):

    def setUp(self):
        super(SystemAdminSecurityGroupTests, self).setUp()
        self.context = self.system_admin_ctx

    def test_create_security_group(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'create_security_group', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'create_security_group', self.alt_target)

    def test_get_security_group(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_group', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_group', self.alt_target)

    def test_get_security_groups_tags(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_groups_tags', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_groups_tags', self.alt_target)

    def test_update_security_group(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'update_security_group', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'update_security_group', self.alt_target)

    def test_update_security_groups_tags(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'update_security_groups_tags', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'update_security_groups_tags', self.alt_target)

    def test_delete_security_group(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_group', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_group', self.alt_target)

    def test_delete_security_groups_tags(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_groups_tags', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_groups_tags', self.alt_target)


class SystemMemberSecurityGroupTests(SystemAdminSecurityGroupTests):

    def setUp(self):
        super(SystemMemberSecurityGroupTests, self).setUp()
        self.context = self.system_member_ctx


class SystemReaderSecurityGroupTests(SystemMemberSecurityGroupTests):

    def setUp(self):
        super(SystemReaderSecurityGroupTests, self).setUp()
        self.context = self.system_reader_ctx


class AdminSecurityGroupTests(SecurityGroupAPITestCase):

    def setUp(self):
        super(AdminSecurityGroupTests, self).setUp()
        self.context = self.project_admin_ctx

    def test_create_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'create_security_group', self.target))
        self.assertTrue(
            policy.enforce(
                self.context, 'create_security_group', self.alt_target))

    def test_get_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'get_security_group', self.target))
        self.assertTrue(
            policy.enforce(
                self.context, 'get_security_group', self.alt_target))

    def test_get_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'get_security_groups_tags',
                           self.target))
        self.assertTrue(
            policy.enforce(self.context, 'get_security_groups_tags',
                           self.alt_target))

    def test_update_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'update_security_group', self.target))
        self.assertTrue(
            policy.enforce(
                self.context, 'update_security_group', self.alt_target))

    def test_update_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'update_security_groups_tags',
                           self.target))
        self.assertTrue(
            policy.enforce(self.context, 'update_security_groups_tags',
                           self.alt_target))

    def test_delete_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'delete_security_group', self.target))
        self.assertTrue(
            policy.enforce(
                self.context, 'delete_security_group', self.alt_target))

    def test_delete_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'delete_security_groups_tags',
                           self.target))
        self.assertTrue(
            policy.enforce(self.context, 'delete_security_groups_tags',
                           self.alt_target))


class ProjectMemberSecurityGroupTests(AdminSecurityGroupTests):

    def setUp(self):
        super(ProjectMemberSecurityGroupTests, self).setUp()
        self.context = self.project_member_ctx

    def test_create_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'create_security_group', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group', self.alt_target)

    def test_get_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'get_security_group', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'get_security_group', self.alt_target)

    def test_get_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'get_security_groups_tags',
                           self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized, policy.enforce,
            self.context, 'get_security_groups_tags', self.alt_target)

    def test_update_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'update_security_group', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'update_security_group', self.alt_target)

    def test_update_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'update_security_groups_tags',
                           self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce, self.context, 'update_security_groups_tags',
            self.alt_target)

    def test_delete_security_group(self):
        self.assertTrue(
            policy.enforce(self.context, 'delete_security_group', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group', self.alt_target)

    def test_delete_security_groups_tags(self):
        self.assertTrue(
            policy.enforce(self.context, 'delete_security_groups_tags',
                           self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized, policy.enforce,
            self.context, 'delete_security_groups_tags', self.alt_target)


class ProjectReaderSecurityGroupTests(ProjectMemberSecurityGroupTests):

    def setUp(self):
        super(ProjectReaderSecurityGroupTests, self).setUp()
        self.context = self.project_reader_ctx

    def test_create_security_group(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group', self.alt_target)

    def test_update_security_group(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'update_security_group', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'update_security_group', self.alt_target)

    def test_update_security_groups_tags(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'update_security_groups_tags', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'update_security_groups_tags', self.alt_target)

    def test_delete_security_group(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group', self.alt_target)

    def test_delete_security_groups_tags(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_groups_tags', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_groups_tags', self.alt_target)


class SecurityGroupRuleAPITestCase(base.PolicyBaseTestCase):

    def setUp(self):
        super(SecurityGroupRuleAPITestCase, self).setUp()
        self.sg = {
            'id': uuidutils.generate_uuid(),
            'project_id': self.project_id}

        self.target = {
            'project_id': self.project_id,
            'security_group_id': self.sg['id'],
            'ext_parent_security_group_id': self.sg['id']}
        self.alt_target = {
            'project_id': self.alt_project_id,
            'security_group_id': self.sg['id'],
            'ext_parent_security_group_id': self.sg['id']}

        self.plugin_mock = mock.Mock()
        self.plugin_mock.get_security_group.return_value = self.sg
        mock.patch(
            'neutron_lib.plugins.directory.get_plugin',
            return_value=self.plugin_mock).start()


class SystemAdminSecurityGroupRuleTests(SecurityGroupRuleAPITestCase):

    def setUp(self):
        super(SystemAdminSecurityGroupRuleTests, self).setUp()
        self.context = self.system_admin_ctx

    def test_create_security_group_rule(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'create_security_group_rule', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'create_security_group_rule', self.alt_target)

    def test_get_security_group_rule(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_group_rule', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'get_security_group_rule', self.alt_target)

    def test_delete_security_group_rule(self):
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_group_rule', self.target)
        self.assertRaises(
            base_policy.InvalidScope,
            policy.enforce,
            self.context, 'delete_security_group_rule', self.alt_target)


class SystemMemberSecurityGroupRuleTests(SystemAdminSecurityGroupRuleTests):

    def setUp(self):
        super(SystemMemberSecurityGroupRuleTests, self).setUp()
        self.context = self.system_member_ctx


class SystemReaderSecurityGroupRuleTests(SystemMemberSecurityGroupRuleTests):

    def setUp(self):
        super(SystemReaderSecurityGroupRuleTests, self).setUp()
        self.context = self.system_reader_ctx


class AdminSecurityGroupRuleTests(SecurityGroupRuleAPITestCase):

    def setUp(self):
        super(AdminSecurityGroupRuleTests, self).setUp()
        self.context = self.project_admin_ctx

    def test_create_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'create_security_group_rule', self.target))
        self.assertTrue(
            policy.enforce(self.context,
                           'create_security_group_rule', self.alt_target))

    def test_get_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'get_security_group_rule', self.target))
        self.assertTrue(
            policy.enforce(self.context,
                           'get_security_group_rule', self.alt_target))

    def test_delete_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'delete_security_group_rule', self.target))
        self.assertTrue(
            policy.enforce(self.context,
                           'delete_security_group_rule', self.alt_target))


class ProjectMemberSecurityGroupRuleTests(AdminSecurityGroupRuleTests):

    def setUp(self):
        super(ProjectMemberSecurityGroupRuleTests, self).setUp()
        self.context = self.project_member_ctx

    def test_create_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'create_security_group_rule', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group_rule', self.alt_target)

    def test_get_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'get_security_group_rule', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'get_security_group_rule', self.alt_target)

    def test_delete_security_group_rule(self):
        self.assertTrue(
            policy.enforce(self.context,
                           'delete_security_group_rule', self.target))
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group_rule', self.alt_target)


class ProjectReaderSecurityGroupRuleTests(ProjectMemberSecurityGroupRuleTests):

    def setUp(self):
        super(ProjectReaderSecurityGroupRuleTests, self).setUp()
        self.context = self.project_reader_ctx

    def test_create_security_group_rule(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group_rule', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'create_security_group_rule', self.alt_target)

    def test_delete_security_group_rule(self):
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group_rule', self.target)
        self.assertRaises(
            base_policy.PolicyNotAuthorized,
            policy.enforce,
            self.context, 'delete_security_group_rule', self.alt_target)
