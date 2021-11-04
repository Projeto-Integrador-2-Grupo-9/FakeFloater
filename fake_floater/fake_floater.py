import paho.mqtt.client as mqtt
import json
import time
from time import gmtime, strftime
import random
import threading

MQTT_BROKER = "test.mosquitto.org"


def on_message(client, userdata, message):

    payload = message.payload.decode("utf-8")
    topic = message.topic

    print(f"[*] message recieved at [{topic}] {payload}", flush=True)


class FakeFloater:

    def __init__(self, mac_address, starting_position):
        self.mac_address = mac_address
        self.starting_position = starting_position
        self.current_position = starting_position
        self.mqtt_client = mqtt.Client(self.mac_address)
        self.mqtt_client.on_message = on_message

    def start(self):
        self.mqtt_client.connect(MQTT_BROKER)
        self.mqtt_client.loop_start()
        self.mqtt_client.publish(
            "AD/devices",
            json.dumps(
                {"new_device": self.mac_address,
                 "starting_position": self.starting_position}
            )
        )

        print("[*] just published " +
              json.dumps({"new_device": self.mac_address})
              + " to Topic AD/devices", flush=True)

        topic = f"AD/devices/{self.mac_address}"
        self.mqtt_client.subscribe(topic)

        print("Just subscribed to " +
              f"AD/devices/{self.mac_address}", flush=True)

        self.watch_sensors()
        self.watch_position()

    def watch_sensors(self):

        threading.Timer(15.0, self.watch_sensors).start()

        dissolved_oxygen = float("{:.2f}".format(random.uniform(6, 12)))
        ph = float("{:.2f}".format(random.uniform(7, 8)))
        temperature = float("{:.2f}".format(random.uniform(20, 23)))
        turbidity = float("{:.2f}".format(random.uniform(45, 50)))
        conductivity = float("{:.0f}".format(random.uniform(25000, 30000)))
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        payload = json.dumps({"device": self.mac_address,
                              "dissolved_oxygen": dissolved_oxygen,
                              "ph": ph,
                              "temperature": temperature,
                              "turbidity": turbidity,
                              "conductivity": conductivity,
                              "timestamp": timestamp})

        self.mqtt_client.publish("AD/sensor_data", payload
                                 )

        print("[*] just published " + payload +
              " to Topic AD/sensor_data", flush=True)

    def watch_position(self):

        threading.Timer(5.0, self.watch_position).start()

        rand_lat = float("{:.4f}".format((random.uniform(-1, 1)/1000) +
                                         self.current_position["lat"]))
        rand_lng = float("{:.4f}".format((random.uniform(-1, 1)/1000) +
                                         self.current_position["lng"]))

        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        self.current_position = {
            "lat": rand_lat,
            "lng": rand_lng
        }

        payload = json.dumps({"device": self.mac_address,
                              "current_position": self.current_position,
                              "timestamp": timestamp}
                             )

        self.mqtt_client.publish("AD/position_data", payload)

        print("[#] just published " + payload +
              " to Topic AD/position_data", flush=True)
