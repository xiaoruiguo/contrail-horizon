# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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

from django.core.urlresolvers import reverse  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import tabs

from openstack_dashboard import api

from contrail_openstack_dashboard.openstack_dashboard.dashboards.project.networking.ports \
    import forms as project_forms
from contrail_openstack_dashboard.openstack_dashboard.dashboards.project.networking.ports \
    import tabs as project_tabs


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.PortDetailTabs
    template_name = 'project/networking/ports/detail.html'


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdatePort
    template_name = 'project/networking/ports/update.html'
    context_object_name = 'port'
    success_url = 'horizon:project:networking:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['network_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            port_id = self.kwargs['port_id']
            try:
                self._object = api.neutron.port_get(self.request, port_id)
            except Exception:
                redirect = reverse("horizon:project:networking:detail",
                                   args=(self.kwargs['network_id'],))
                msg = _('Unable to retrieve port details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        port = self._get_object()
        context['port_id'] = port['id']
        context['network_id'] = port['network_id']
        return context

    def get_initial(self):
        port = self._get_object()
        return {'port_id': port['id'],
                'network_id': port['network_id'],
                'tenant_id': port['tenant_id'],
                'name': port['name'],
                'admin_state': port['admin_state_up'],
                'device_id': port['device_id'],
                'device_owner': port['device_owner']}
