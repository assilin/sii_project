import paho.mqtt.client as mqtt
import logging
from datetime import datetime
import sys
import topics
import phrases


logging.basicConfig(filename='weather_subscriber.log', level=logging.INFO)

# MQTT define
MQTT_BROKER = 'f0edb4f566e04d5bafb7b1753f59da72.s2.eu.hivemq.cloud'


def on_connect(client, userdata, flags, rc, properties=None):
    """Connect callback."""
    client.subscribe(topic, qos=1)
    logging.info(f'{datetime.now()} - CONNACK received with code {rc}.')


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """Subscribe callback."""
    logging.info(f'{datetime.now()} - Subscribed: {str(mid)} {str(granted_qos)}')


def on_message(client, userdata, msg):
    """Message callback."""
    mqtt_response = msg.payload.decode()
    print(f'{datetime.now()}\n{mqtt_response}\n')
    logging.info(f'{datetime.now()} - Received message: {mqtt_response}.')


def check_topic(query):
    """Check topic's sintax"""
    if len(query) < 2 or len(query) > 4:
        return 0

    if query[1] == 'forecast':
        if len(query) == 2:
            topic = f'{query[1]}/city/#'
        else:
            topic = f'{query[1]}/city/{query[2]}'

    elif query[1] == 'current':
        if len(query) == 2:
            topic = f'{query[1]}/city/#'
        elif len(query) == 3:
            topic = f'{query[1]}/city/{query[2]}/metric/#'
        else:
            topic = f'{query[1]}/city/{query[2]}/metric/{query[3]}'
    else:
        return 0

    if topic not in topics.topics_pub:
        return 0

    return topic


if __name__ == '__main__':

    client = mqtt.Client()
    client.on_connect = on_connect

    # setting callbacks
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

    # set username and password
    client.username_pw_set('bot_request', 'Test1234')

    # connect to HiveMQ Cloud on port 8883
    client.connect(MQTT_BROKER, 8883)
    # client.loop_start()

    query = []
    for arg in sys.argv:
        query.append(arg)

    topic = check_topic(query)
    if not topic:
        print(phrases.error_args)
        sys.exit(1)

    client.loop_forever()
