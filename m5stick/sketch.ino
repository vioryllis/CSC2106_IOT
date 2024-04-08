#include "M5StickCPlus.h"
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "raidensupremacy";
const char* password = "matchasupremacy";
const char* mqtt_server = "172.20.10.10";

void setupWifi();
void callback(char* topic, byte* payload, unsigned int length);
void reConnect();

void setup() {
  M5.begin();
  M5.Lcd.setRotation(3);
  pinMode(M5_LED, OUTPUT);
  setupWifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.begin(115200); // Initialize serial communication

  if (!client.connected()) {
    reConnect();
  }
  client.loop();

  // Publish a message once after setup
  char msg[] = "Hello from M5StickC Plus";
  M5.Lcd.print("Publish message: ");
  M5.Lcd.println(msg);
  client.publish("M5Stack", msg);
}

void loop() {
  if (!client.connected()) {
    reConnect();
  }
  client.loop();

  M5.update(); // This line is necessary to update the button state

  // Check if the home button (BtnA) is pressed
  if (M5.BtnA.wasPressed()) {
    M5.Lcd.fillScreen(BLACK); // Clear the LCD screen
    M5.Lcd.setCursor(0, 0); // Reset the cursor to the top-left corner
  }

  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming message
    String message = Serial.readStringUntil('\n');

    // Publish the message
    client.publish("M5Stack", message.c_str());

    // Display the message on the LCD
    M5.Lcd.print("Sent message: ");
    M5.Lcd.println(message);
  }
}

void setupWifi() {
  delay(10);
  M5.Lcd.printf("Connecting to %s", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    M5.Lcd.print(".");
  }
  M5.Lcd.printf("\nSuccess\n");
}

void callback(char* topic, byte* payload, unsigned int length) {
  M5.Lcd.print("Message arrived [");
  M5.Lcd.print(topic);
  M5.Lcd.print("] ");
  String message = "";
  for (int i = 0; i < length; i++) {
    M5.Lcd.print((char)payload[i]);
    message += (char)payload[i];
  }
  if (message == "1") {
    digitalWrite(M5_LED, 0);
    M5.Lcd.println("LED ON");
  } else if (message == "0") {
    digitalWrite(M5_LED, 1);
    M5.Lcd.println("LED OFF");
  }
  M5.Lcd.println();
}

void reConnect() {
  while (!client.connected()) {
    M5.Lcd.print("Attempting MQTT connection...");
    String clientId = "M5StickCPlus-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      M5.Lcd.printf("\nSuccess\n");
      client.subscribe("M5Stack/1");
    } else {
      M5.Lcd.print("failed, rc=");
      M5.Lcd.print(client.state());
      M5.Lcd.println("try again in 5 seconds");
      delay(5000);
    }
  }
}
