from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet
import config
import datetime

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
#print(res.message_count)
total_message_count = sub1.message_count + sub2.message_count

scale_by = 0
# Check if scaling is needed
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
