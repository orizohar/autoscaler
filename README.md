# Custom Azure VM Scale Set Autoscaling #

Azure VM scale sets can be configured to autoscale by a variety of metrics but in some scenarios a custom metric is needed. For example, an Azure VMSS might be running a set of workers consuming jobs from several ServiceBus subscriptions and should scale according to the total number of messages in all subscriptions. This repo includes python reference code for a custom autoscaling service for Azure VM scale sets. The code can be run as a time triggered Azure Function or can be run as a service running in a Docker container. 

Although this code implements custom scaling according to a specific scenario (total number of messages in a number of subscriptions), it can be used as a reference for other similar scenarios.

The scenario addressed in this repo is described by the following diagram:

![Diagram](/resources/autoscaler.png)

## Configuration ##

All of the scaler configurations can be found in `config.json`. Values should be changed to fit the VMSS to be scaled and ServiceBus
to be polled.

Also, the service uses an Azure service prinicipal that should be created and given a Contributor role to be able to scale the VMSS (see [this article](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal)).
The service uses the following environment variables for Azure authentication:

- *AZURE_CLIENT_ID* 
- *AZURE_CLIENT_SECRET*
- *AZURE_TENANT_ID*
- *SUBSCRIPTION_ID*

The values for the above variables are provided by the service principal.

Additional environment variables can be defined to override `config.json` values:

- *LOOP*
- *INTERVAL_IN_SEC*
- *SCALING_MIN_CAPACITY*
- *SCALING_MAX_CAPACITY*
- *SCALING_LOW_THRESHOLD*
- *SCALING_HIGH_THRESHOLD*
- *SCALING_UP_FACTOR*
- *SCALING_DOWN_FACTOR*

## Deployment using Docker ##

A Docker image of this application can be created using the included `Dockerfile`. To define the credentials inside the container an environment variables file can be used when running the container.

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
SCALING_MIN_CAPACITY=4
SCALING_MAX_CAPACITY=20
```

## Deployment using Azure Functions ##

The autoscaling service can be also be deployed using Azure Functions. This repository is structured in a way which allows continuous deployment with local git or GitHub deployment sources (for more info, please see [this article](https://docs.microsoft.com/en-us/azure/azure-functions/functions-continuous-deployment)). Note that `function.json` defines a function with a time trigger.

As mentioned above, the service expects credential information to be available via environment variables. Environment variables can be configured by going to **Function app settings --> Configure app settings** from the Function blade and configuring the variables like so:

![Function app settings](/resources/func-appsettings.png)

## Message client ##
The repo also includes an example message client which can be used for sending and receiving messages to/from ServiceBus for testing. See usage information by running: 

```
python msg_client.py --help
```

## References ##
- [VM Scale Sets](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-overview)
- [ServiceBus topics and subscriptions](https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-topics-subscriptions)
- [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Azure Python SDK on GitHub](https://github.com/Azure/azure-sdk-for-python)
