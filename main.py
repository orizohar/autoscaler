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
    parser.add_argument('-r','--run_once', help='Optional flag to indicate polling and scaling should run once. Overrides config file.', action='store_true')
    parser.add_argument('-i','--interval', help='Integer number of seconds between subscriptions polling. Overrides config file', type=int)
    
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

def env_override(config_data):
    '''
    Override configuration with environment variables if they exist.
    '''
    config_data['run_once'] = bool(os.getenv('RUN_ONCE', config_data['run_once']))
    config_data['polling_interval_seconds'] = float(os.getenv('INTERVAL_IN_SEC', config_data['polling_interval_seconds']))
    scaling_params = config_data['autoscaling_parameters']
    scaling_params['min_capacity'] = os.getenv('SCALING_MIN_CAPACITY', scaling_params['min_capacity'])
    scaling_params['max_capacity'] = os.getenv('SCALING_MAX_CAPACITY', scaling_params['max_capacity'])
    scaling_params['low_message_threshold'] = os.getenv('SCALING_LOW_THRESHOLD', scaling_params['low_message_threshold'])
    scaling_params['high_message_threshold'] = os.getenv('SCALING_HIGH_THRESHOLD', scaling_params['high_message_threshold'])
    scaling_params['scale_up_factor'] = os.getenv('SCALING_UP_FACTOR', scaling_params['scale_up_factor'])
    scaling_params['scale_down_factor'] = os.getenv('SCALING_DOWN_FACTOR', scaling_params['scale_down_factor'])

def args_override(config_data, args):
    '''
    Override configuration with command line arguments if they exist.
    '''
    if args.run_once:
        config_data['run_once'] = True
    if args.interval:
        config_data['polling_interval_seconds'] = args.interval

if __name__ == "__main__":
    main()
