import serial
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import uuid
import datetime
import requests, sys

clientId = "Omega_AC51"
endpoint = "a1km12bi5nlxfi-ats.iot.us-east-1.amazonaws.com"
rootCAFilePath = "/IOT/lab8/certs/Amazon-root-CA-1.pem"
privateKeyFilePath = "/IOT/lab8/certs/private.pem.key"
certFilePath = "/IOT/lab8/certs/device.pem.crt"

myMQTTClient = AWSIoTMQTTClient(clientId)

myMQTTClient.configureEndpoint(endpoint, 8883)

# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH", "PRIVATE/KEY/PATH", "CERTIFICATE/PATH")
myMQTTClient.configureCredentials(rootCAFilePath, privateKeyFilePath, certFilePath)
# For Websocket, we only need to configure the root CA
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

topic = "OmegaAC51/data/project"

QoS = 1

def customCallback(client, userdata, message):
    print(str(message.topic) + ": " + str(message.payload))


def customOnMessage(client, userdata, message):
    print(str(message.topic) + ": " + str(message.payload))


print("Connecting to: " + endpoint + " with ClientID " + clientId)

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)


myMQTTClient.unsubscribe(topic)
print("Unsuscribed and Disconnected")
myMQTTClient.disconnect()

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)
myMQTTClient.unsubscribe(topic)
print("Unsuscribed and Disconnected")
myMQTTClient.disconnect()

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)
myMQTTClient.unsubscribe(topic)
print("Unsuscribed and Disconnected")
myMQTTClient.disconnect()

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)
myMQTTClient.unsubscribe(topic)
print("Unsuscribed and Disconnected")
myMQTTClient.disconnect()

connect_ACK = myMQTTClient.connect()
print("Connected!")
print("Subscribing to topic: ", topic)
myMQTTClient.subscribe(topic, QoS, customOnMessage)
print("Subscribed with QoS: ", QoS)
myMQTTClient.unsubscribe(topic)
print("Unsuscribed and Disconnected")
myMQTTClient.disconnect()
