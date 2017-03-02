from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachineScaleSet
import config

credentials = ServicePrincipalCredentials(
            client_id=config.AZURE_CLIENT_ID,
            secret=config.AZURE_CLIENT_SECRET,
            tenant=config.AZURE_TENANT_ID
)

subscription_id = config.SUBSCRIPTION_ID

sbmgmt = ServiceBusManagementClient(credentials, subscription_id)
res = sbmgmt.subscriptions.get('sb-rg', config.SB_NAMESPACE , 't1', 's10')
print(res.message_count)

cmgmt = ComputeManagementClient(credentials, subscription_id)
vmss = cmgmt.virtual_machine_scale_sets.get('vmssdemo', 'vmss01')
print(vmss.sku)
vmss_new = VirtualMachineScaleSet(vmss.location, sku=vmss.sku)
vmss_new.sku.capacity = 5L
print(vmss_new.sku)
poller  = cmgmt.virtual_machine_scale_sets.create_or_update('vmssdemo', 'vmss01', vmss_new)
res = poller.result()
print(res)
