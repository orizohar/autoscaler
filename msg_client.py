import argparse
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
import os

class MessageClient():
    def __init__(self, namespace, keyname, keyval):
        self._client = ServiceBusService(
            service_namespace=namespace,
            shared_access_key_name=keyname,
            shared_access_key_value=keyval)

    def send(self, topic, num):
        for i in range(num):
            msg = Message('Msg {0}'.format(i).encode('utf-8'), custom_properties={'messagenumber':i})
            self._client.send_topic_message(topic, msg)
            print ('Sending message {0}'.format(i))
    
    def receive(self, topic, subscription, num):
        for i in range(num):
            msg = self._client.receive_subscription_message(topic, subscription, peek_lock=False, timeout=10)
            print(msg.body)

def main():
    parser = argparse.ArgumentParser(description='Send or receive ServiceBus messages')
    parser.add_argument('-m','--mode', help='s or r to set send or recieve mode.', required=True, choices=['s','r'])
    parser.add_argument('-n','--num', help='number of messages to send/receive. Optional. default 1', type=int, required=False, default=1)
    parser.add_argument('--namespace', help='ServiceBus namespace', required=False, default=os.getenv('SB_NAMESPACE'))
    parser.add_argument('--keyname', help='ServiceBus key name', required=False, default=os.getenv('SB_KEYNAME'))
    parser.add_argument('--keyval', help='ServiceBus key value', required=False, default=os.getenv('SB_KEYVAL'))
    parser.add_argument('-t', '--topic', help='Topic to use for sending/receiving', required=True)
    parser.add_argument('-s', '--subscription', help='Subscription to receive messages from', required=False)

    args = parser.parse_args()
    if (not args.namespace) or (not args.keyname) or (not args.keyval):
        print('ERROR: Service Bus namespace, key name or key value missing please define the following environment variables:')
        print('\tSB_NAMESPACE, SB_KEYNAME, SB_KEYVAL')
        print('Or alternatively provide the following arguments')
        print('\t--namespace, --keyname, --keyval')
        print('Exiting...')
        exit(1)


    msg_client = MessageClient(args.namespace, args.keyname, args.keyval)
    if args.mode == 's':
        msg_client.send(args.topic, args.num)
    else:
        msg_client.receive(args.topic, args.subscription, args.num)

if __name__ == "__main__":
    main()
