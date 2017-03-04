# Custom Azure VM Scale Set Autoscaling #

This repo includes python code for a custom autoscaling service for Azure VM scale sets. The code can be run as a time triggered Azure Function or can be run as a service running in a Docker container (hosted on a Linux App Service instance for example). The service autoscales the VMSS according to the sum of messages in two Azure ServiceBus subscriptions.

## Configuration ##

All of the scaler configurations can be found in `config.py`. You can change these to hardcoded ones for you environment or define them using environment variables. Please note that for the code to work you will need to define these values:

1. Your Azure subscription ID and tenant ID.
2. Create a service principal (see [this article](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal)) and add its credentials `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET`. Note you will need to give the app you create a contributor role to be able to scale the VMSS.
3. Your vm scale set resource group and name
4. Your ServiceBus namespace with two subscriptions which belong to two topics.

Optionally you can change the scaling parameters (min/max capacity, scaling factor, scale action thresholds) in `config.py`

Note that if the environment variable `RUN_ONCE` is defined the autoscaling logic will run once (e.g. for running via Azure Functions).

## Running via a Docker container ##
You can build a docker image of this application using the included `Dockerfile`. Be sure to change `config.py` with your own configuration or run the container with an environment variables file.

Example docker run command:

```sh
docker run -d --name scaler --env-file ./env.list orizohar/autoscaler
```

Example of `env.list`:

```
AZURE_CLIENT_ID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
AZURE_CLIENT_SECRET=1111111111111111111111111111111111111111111=
AZURE_TENANT_ID=YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY
SUBSCRIPTION_ID=ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZZ
VMSS_RESOURCE_GROUP=vmss-rg
VMSS_NAME=myvmss
SB_RESOURCE_GROUP=sb-rg
SB_NAMESPACE=myservicebus
SB_KEYNAME=mysbkey
SB_KEYVAL=2222222222222222222222222222222222222222222=
SB_TOPIC_1=topic1
SB_TOPIC_2=topic2
SB_SUBSCRIPTION_1=sub1
SB_SUBSCRIPTION_2=sub2
```

## Message client ##
The repo also includes an example message client which can help you with sending and receiving messages to/from ServiceBus for testing. Run the following for more options 

```
python msg_client.py --help
```

## References ##
- [VM Scale Sets](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-overview)
- [ServiceBus topics and subscriptions](https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-topics-subscriptions)
- [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Azure Python SDK on GitHub](https://github.com/Azure/azure-sdk-for-python)
