# Copyright (c) 2014 Cisco Systems Inc.
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

from nova.scheduler.filters import aggregate_image_properties_isolation
from nova.scheduler.solvers import constraints


class AggregateImagePropertiesIsolationConstraint(
                                            constraints.BaseLinearConstraint):
    """AggregateImagePropertiesIsolation works with image properties."""

    def _generate_components(self, variables, hosts, filter_properties):
        num_hosts = len(hosts)
        num_instances = filter_properties.get('num_instances')

        var_matrix = variables.host_instance_matrix

        host_filter = aggregate_image_properties_isolation.\
                            AggregateImagePropertiesIsolation()
        for i in xrange(num_hosts):
            host_passes = host_filter.host_passes(hosts[i], filter_properties)
            if not host_passes:
                for j in xrange(num_instances):
                    self.variables.append([var_matrix[i][j]])
                    self.coefficients.append([1])
                    self.constants.append(0)
                    self.operators.append('==')
