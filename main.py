from custom_auto_scaler import CustomAutoScaler
import time
import os
import argparse
import json

AZURE_CLIENT_ID=os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET=os.getenv('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID=os.getenv('AZURE_TENANT_ID')
SUBSCRIPTION_ID=os.getenv('SUBSCRIPTION_ID')
SCALER_CONFIG_FILEPATH=os.getenv('SCALER_CONFIG_FILEPATH', 'config.json')

def main():
    parser = argparse.ArgumentParser(description='Autoscaling service polling multiple ServiceBus subscriptions')
    parser.add_argument('-f','--file', help='JSON config file path', default='config.json')
    parser.add_argument('-r','--run_once', help='Optional flag to indicate polling and scaling should run once. Overrides config file option.', action='store_true')
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        print("ERROR: Can't find {0} - Exiting.".format(args.file))
    verify_credential_data()
    file_content = open(args.file).read()
    config_data = json.loads(file_content)

    env_override(config_data)
    args_override(config_data, args)

    scaler = CustomAutoScaler(
        AZURE_CLIENT_ID,
        AZURE_CLIENT_SECRET,
        AZURE_TENANT_ID,
        SUBSCRIPTION_ID,
        config_data)    
    scaler.run()
    if config_data['run_once'] :
        return
    while True:
        time.sleep(config_data['polling_interval_seconds'])
        scaler.run()

def verify_credential_data():
    credential_data = [AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, SUBSCRIPTION_ID]
    verified = all(v is not None for v in credential_data)
    if not verified:
        print('Missing credential information. Please make sure the following env vars are defined:')
        print('\tAZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, SUBSCRIPTION_ID')
        print('Exiting')
        exit(1)

def env_override(config):
    '''
    Override configuration with environment variables if they exist.
    '''
    pass

def args_override(config, args):
    '''
    Override configuration with arguments if they exist.
    '''
    if args.run_once:
        config_data['run_once'] = True

if __name__ == "__main__":
    main()
