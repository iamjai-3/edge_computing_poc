import threading
import uuid

import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient

# MQTT Broker (Broker address and port)
MQTT_BROKER = ""
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

# MQTT Topics to subscribe to (you can add more topics as needed)
TOPICS = ["edge/temp"]


# Azure IoT Hub connection string
IOTHUB_CONNECTION_STRING = "HostName=EdgeComputing.azure-devices.net;DeviceId=rpi-edge;SharedAccessKey=fKwRhSi4fIonj61wsSzV55GmiS3j4WxzKf+wSsvIcqo="
client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_CONNECTION_STRING)

# Callback when the client connects to the broker
def on_connect(client, userData, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with result code: {rc}")
        for topic in TOPICS:
            client.subscribe(topic)
    else:
        print(f"Connection failed with result code: {rc}")


# Callback when a message is received from the broker
def on_message(client, userData, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    print(f"Received message on topic '{topic}': {payload}")

    # Acknowledge receipt to the sender (publish an acknowledgment message)
    # You can customize the acknowledgment message as per your use case
    # For example, send an ACK with the topic + "/ack" and a specific payload.
    acknowledgment_topic = topic + "/ack"
    acknowledgment_payload = "Received"
    client.publish(acknowledgment_topic, acknowledgment_payload)

    # Send data to Azure IoT Hub
    send_to_azure(payload)
    
def send_to_azure(data):
    try:
        # Send the data to Azure IoT Hub
        client.send_message(data)
        print("Message sent to Azure IoT Hub")
    except Exception as e:
        print(f"Error sending data to Azure IoT Hub: {e}")

def mqtt_thread():
    client_id = f"mqtt-client-{uuid.uuid4()}"  # Generate a unique client ID
    client = mqtt.Client(client_id=client_id, clean_session=False)  # Persistent session
    client.username_pw_set(
        username=MQTT_USERNAME, password=MQTT_PASSWORD
    )  # Set username and password
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Disconnecting MQTT client...")
        client.disconnect()


if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=mqtt_thread)

    try:
        mqtt_thread.start()
        # Your main application logic here...
        mqtt_thread.join()  # Wait for the MQTT thread to finish before exiting.
    except KeyboardInterrupt:
        print("Exiting...")
        mqtt_thread.join()  # Wait for the MQTT thread to finish before exiting.
        mqtt_thread.join()  # Wait for the MQTT thread to finish before exiting.
