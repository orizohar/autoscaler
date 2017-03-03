import argparse
import config
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME

class MessageClient():
    def __init__(self, namespace, keyname, keyval):
        self._client = ServiceBusService(
            service_namespace=config.SB_NAMESPACE,
            shared_access_key_name=config.SB_KEYNAME,
            shared_access_key_value=config.SB_KEYVAL)

    def send(self, topic, num):
        for i in range(num):
            msg = Message('Msg {0}'.format(i).encode('utf-8'), custom_properties={'messagenumber':i})
            self._client.send_topic_message(topic, msg)
            print ('Sending message {0}'.format(i))
    
    def receive(self, topic, subscription, num):
        for i in range(num):
            msg = self._client.receive_subscription_message(topic, subscription, peek_lock=False)
            print(msg.body)

def main():
    parser = argparse.ArgumentParser(description='Send or receive ServiceBus messages')
    parser.add_argument('-m','--mode', help='s or r to set send or recieve mode.', required=True, choices=['s','r'])
    parser.add_argument('-n','--num', help='number of messages to send/receive. Optional. default 1', type=int, required=False, default=1)
    parser.add_argument('--namespace', help='ServiceBus namespace', required=False, default=config.SB_NAMESPACE)
    parser.add_argument('--keyname', help='ServiceBus key name', required=False, default=config.SB_KEYNAME)
    parser.add_argument('--keyval', help='ServiceBus key value', required=False, default=config.SB_KEYVAL)
    parser.add_argument('-t', '--topic', help='Topic to use for sending/receiving', required=False, default=config.SB_TOPIC_1)
    parser.add_argument('-s', '--subscription', help='Subscription to receive messages from', required=False, default=config.SB_SUBSCRIPTION_1)

    args = parser.parse_args()
    msg_client = MessageClient(args.namespace, args.keyname, args.keyval)
    if args.mode == 's':
        msg_client.send(args.topic, args.num)
    else:
        msg_client.receive(args.topic, args.subscription, args.num)

if __name__ == "__main__":
    main()



