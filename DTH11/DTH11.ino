#include "DHT.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define DHTTYPE DHT11 // DHT 11 SENSOR
#define dht_dpin 0

DHT dht(dht_dpin, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

// WiFi
const char *ssid = "";     // Enter your WiFi name
const char *password = ""; // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "";
const char *topic = "edge/temp";
const char *mqtt_user = "";
const char *mqtt_password = "";
const int mqtt_port = 1883;

void setup(void)
{
  dht.begin();
  Serial.begin(9600);
  Serial.println("Humidity and temperature\n\n");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  while (!client.connected())
  {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password))
    {
      Serial.println("Connected to MQTT");
    }
    else
    {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  Serial.printf("Current humidity = %.2f%%  temperature = %.2fC\n", h, t);

  // Create a JSON object and serialize it to a string
  StaticJsonDocument<100> jsonDocument; // Adjust the size as needed
  jsonDocument["humidity"] = h;
  jsonDocument["temperature"] = t;
  String jsonString;
  serializeJson(jsonDocument, jsonString);

  // Publish humidity and temperature to MQTT
  client.publish(topic, jsonString.c_str());

  delay(800);
}

void callback(char *topic, byte *payload, unsigned int length)
{
  // Handle incoming MQTT messages here if needed
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password))
    {
      Serial.println("Connected to MQTT");
    }
    else
    {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}