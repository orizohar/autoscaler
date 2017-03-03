from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet
import config
import datetime

class CustomAutoScaler():
    def __init__(self, app_id, app_secret, tenant_id, subscription_id):
        credentials = ServicePrincipalCredentials(
            client_id=app_id,
            secret=app_secret,
            tenant=tenant_id) 
        self._sb_mgr = ServiceBusManagementClient(credentials, subscription_id)
        self._compute_mgr = ComputeManagementClient(credentials, subscription_id)

    def poll_total_messages(self):
        sub1 = self._sb_mgr.subscriptions.get(config.SB_RESOURCE_GROUP, 
            config.SB_NAMESPACE , 
            config.SB_TOPIC_1, 
            config.SB_SUBSCRIPTION_1)
        sub2 = self._sb_mgr.subscriptions.get(config.SB_RESOURCE_GROUP, 
            config.SB_NAMESPACE , 
            config.SB_TOPIC_2, 
            config.SB_SUBSCRIPTION_2)
        total_message_count = sub1.message_count + sub2.message_count
        return total_message_count

    def get_vmss_info(self):
        vmss = self._compute_mgr.virtual_machine_scale_sets.get(config.VMSS_RESOURCE_GROUP, config.VMSS_NAME)
        return vmss

    def scale_vmss(self, vmss, new_capacity):
        vmss_new = VirtualMachineScaleSet(vmss.location, sku=vmss.sku)
        vmss_new.sku.capacity = new_capacity
        scaling_action  = self._compute_mgr.virtual_machine_scale_sets.create_or_update(config.VMSS_RESOURCE_GROUP, config.VMSS_NAME, vmss_new)
        res = scaling_action.result()
        return res

    def run(self, low, high, scale_down_amount, scale_up_amount, min_capacity, max_capacity):
        total_message_count = self.poll_total_messages()
        # Check if scaling is needed
        scale_by = 0
        if total_message_count < low:
            scale_by = -scale_down_amount
        elif total_message_count > high:
            scale_by = scale_up_amount
        vmss = self.get_vmss_info()
        new_capacity = vmss.sku.capacity + scale_by
        # Verify new scale does not go over or under allowed capacity
        new_capacity = max (new_capacity, min_capacity)
        new_capacity = min (new_capacity, max_capacity)
        # Scale if needed
        if new_capacity != vmss.sku.capacity:
            print('Scaling is needed. Attempting to scale {0}-->{1}'.format(vmss.sku.capacity, new_capacity))
            res = self.scale_vmss(vmss, new_capacity)
            print('Provisioning state: {0}'.format(res.provisioning_state))
        else:
            print('No scaling needed. Current scale: {0}'.format(vmss.sku.capacity))

'''
# Service principal credentials to be used by clients for Azure authentication
credentials = ServicePrincipalCredentials(
            client_id=config.AZURE_CLIENT_ID,
            secret=config.AZURE_CLIENT_SECRET,
            tenant=config.AZURE_TENANT_ID
)

# Use the ServiceBus managent client to poll for subscriptions' data.
sbmgmt = ServiceBusManagementClient(credentials, config.SUBSCRIPTION_ID)
sub1 = sbmgmt.subscriptions.get(config.SB_RESOURCE_GROUP, 
    config.SB_NAMESPACE , 
    config.SB_TOPIC_1, 
    config.SB_SUBSCRIPTION_1)
sub2 = sbmgmt.subscriptions.get(config.SB_RESOURCE_GROUP, 
    config.SB_NAMESPACE , 
    config.SB_TOPIC_2, 
    config.SB_SUBSCRIPTION_2)
total_message_count = sub1.message_count + sub2.message_count

# Check if scaling is needed
scale_by = 0
if total_message_count < config.VMSS_LOW_THRESHOLD:
    scale_by = -config.VMSS_SCALE_DOWN_BY
elif total_message_count > config.VMSS_HIGH_THRESHOLD:
    scale_by = config.VMSS_SCALE_UP_BY

# Use compute clinet to poll VM Scale Set data
cmgmt = ComputeManagementClient(credentials, config.SUBSCRIPTION_ID)
vmss = cmgmt.virtual_machine_scale_sets.get(config.VMSS_RESOURCE_GROUP, config.VMSS_NAME)

new_capacity = vmss.sku.capacity + scale_by

# Verify new scale does not go over or under allowed capacity
new_capacity = max (new_capacity, config.VMSS_MIN_CAPACITY)
new_capacity = min (new_capacity, config.VMSS_MAX_CAPACITY)

# Scale if needed
if new_capacity != vmss.sku.capacity:
    print('Scaling is needed. Attempting to scale {0}-->{1}'.format(vmss.sku.capacity, new_capacity))
    vmss_new = VirtualMachineScaleSet(vmss.location, sku=vmss.sku)
    vmss_new.sku.capacity = new_capacity
    scaling_action  = cmgmt.virtual_machine_scale_sets.create_or_update(config.VMSS_RESOURCE_GROUP, config.VMSS_NAME, vmss_new)
    res = scaling_action.result()
    print('Provisioning state: {0}'.format(res.provisioning_state))
else:
    print('No scaling needed. Current scale: {0}'.format(vmss.sku.capacity))
'''