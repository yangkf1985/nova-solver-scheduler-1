# Copyright (c) 2014 Cisco Systems, Inc.
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

import mock

from nova.pci import pci_stats
from nova.scheduler import solvers
from nova.scheduler.solvers.constraints import pci_passthrough_constraint
from nova import test
from nova.tests.scheduler import solver_scheduler_fakes as fakes


class TestPciPassthroughConstraint(test.NoDBTestCase):

    def setUp(self):
        super(TestPciPassthroughConstraint, self).setUp()
        self.constraint_cls = \
                        pci_passthrough_constraint.PciPassthroughConstraint
        self._generate_fake_constraint_input()

    def _generate_fake_constraint_input(self):
        self.fake_variables = solvers.BaseVariables()
        self.fake_variables.host_instance_matrix = [
                ['h0i0', 'h0i1'],
                ['h1i0', 'h1i1'],
                ['h2i0', 'h2i1']]
        requests = [{'count': 1, 'spec': [{'vendor_id': '8086'}]}]
        self.fake_filter_properties = {
                'pci_requests': requests,
                'instance_uuids': ['fake_uuid_%s' % x for x in range(2)],
                'num_instances': 2}
        host1 = fakes.FakeSolverSchedulerHostState('host1', 'node1',
                {'pci_stats': pci_stats.PciDeviceStats()})
        host2 = fakes.FakeSolverSchedulerHostState('host2', 'node1',
                {'pci_stats': pci_stats.PciDeviceStats()})
        host3 = fakes.FakeSolverSchedulerHostState('host3', 'node1',
                {'pci_stats': pci_stats.PciDeviceStats()})
        self.fake_hosts = [host1, host2, host3]

    @mock.patch('nova.pci.pci_stats.PciDeviceStats.support_requests')
    @mock.patch('nova.pci.pci_stats.PciDeviceStats.apply_requests')
    def test_pci_passthrough_constraint_get_components(self, apl_reqs, spt_reqs):
        spt_reqs.side_effect = [True, False] + [False] + [True, True, False]
        expected_cons_vars = [['h0i1'], ['h1i0'], ['h1i1']]
        expected_cons_coeffs = [[1], [1], [1]]
        expected_cons_consts = [0, 0, 0]
        expected_cons_ops = ['==', '==', '==']
        cons_vars, cons_coeffs, cons_consts, cons_ops = (
                self.constraint_cls().get_components(self.fake_variables,
                self.fake_hosts, self.fake_filter_properties))
        self.assertEqual(expected_cons_vars, cons_vars)
        self.assertEqual(expected_cons_coeffs, cons_coeffs)
        self.assertEqual(expected_cons_consts, cons_consts)
        self.assertEqual(expected_cons_ops, cons_ops)
