# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

import sys
import Adafruit_DHT
import time
from board import SCL, SDA
import busio
from adafruit_seesaw.seesaw import Seesaw

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a11gp9k0yoq3ar-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "RB_Raspi"
PATH_TO_CERT = "certificates/cbce6247dc-certificate.pem.crt"
PATH_TO_KEY = "certificates/cbce6247dc-private.pem.key"
PATH_TO_ROOT = "certificates/AmazonRootCA1.pem"
MESSAGE = "Hello World"
TOPIC = "CMPE181/project"
RANGE = 20

while True:
    i2c_bus = busio.I2C(SCL, SDA)
    ss = Seesaw(i2c_bus, addr=0x36)
    sensor = Adafruit_DHT.AM2302
    pin = 4

    soil_moisture = ss.moisture_read()
    soil_temperature = ss.get_temp()
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=ENDPOINT,
                cert_filepath=PATH_TO_CERT,
                pri_key_filepath=PATH_TO_KEY,
                client_bootstrap=client_bootstrap,
                ca_filepath=PATH_TO_ROOT,
                client_id=CLIENT_ID,
                clean_session=False,
                keep_alive_secs=10
                )
    print("Connecting to {} with client ID '{}'...".format(
            ENDPOINT, CLIENT_ID))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    # Publish message to server desired number of times.
    print('Begin Publish')

    # for i in range (RANGE):
    # data = "{} [{}]".format(MESSAGE, i+1)
    # message = {"message" : data}
    message = {
        "deviceID" : "RB_Raspi",
        "soil_moisture" : soil_moisture,
        "soil_temperature" : soil_temperature,
        "humidity" : humidity,
        "temperature" : temperature
    }
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'CMPE181/project'")
    t.sleep(0.1)

    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()