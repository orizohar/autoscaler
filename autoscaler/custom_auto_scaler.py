import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'env/Lib/site-packages')))
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet
import datetime

class CustomAutoScaler():
    def __init__(self, app_id, app_secret, tenant_id, subscription_id, config_data):
        credentials = ServicePrincipalCredentials(
            client_id=app_id,
            secret=app_secret,
            tenant=tenant_id) 
        self._sb_mgr = ServiceBusManagementClient(credentials, subscription_id)
        self._compute_mgr = ComputeManagementClient(credentials, subscription_id)
        self._config = config_data

    def poll_total_messages(self):
        total_message_count = 0
        for s in self._config['subscriptions']:
            sub_data = self._sb_mgr.subscriptions.get(
                s['resource_group'], 
                s['namespace'] , 
                s['topic'], 
                s['subscription'])
            total_message_count += sub_data.message_count
        return total_message_count

    def get_vmss_info(self):
        vmss = self._compute_mgr.virtual_machine_scale_sets.get(self._config['vmss']['resource_group'], self._config['vmss']['name'])
        return vmss

    def scale_vmss(self, vmss, new_capacity):
        vmss_new = VirtualMachineScaleSet(vmss.location, sku=vmss.sku)
        vmss_new.sku.capacity = new_capacity
        scaling_action  = self._compute_mgr.virtual_machine_scale_sets.create_or_update(
            self._config['vmss']['resource_group'], self._config['vmss']['name'], vmss_new)
        res = scaling_action.result()
        return res

    def run(self):
        params = self._config['autoscaling_parameters']
        total_message_count = self.poll_total_messages()
        # Check if scaling is needed
        scale_by = 0
        if total_message_count < params['low_message_threshold']:
            scale_by = -params['scale_down_factor']
        elif total_message_count > params['high_message_threshold']:
            scale_by = params['scale_up_factor']
        vmss = self.get_vmss_info()
        new_capacity = vmss.sku.capacity + scale_by
        # Verify new scale does not go over or under allowed capacity
        new_capacity = max (new_capacity, params['min_capacity'])
        new_capacity = min (new_capacity, params['max_capacity'])
        # Scale if needed
        if new_capacity != vmss.sku.capacity:
            print('Scaling is needed. Attempting to scale {0}-->{1}'.format(vmss.sku.capacity, new_capacity))
            res = self.scale_vmss(vmss, new_capacity)
            print('Provisioning state: {0}'.format(res.provisioning_state))
        else:
            print('No scaling needed. Current scale: {0}'.format(vmss.sku.capacity))
