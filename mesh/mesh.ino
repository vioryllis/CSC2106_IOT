#include <WiFi.h>
#include <HTTPClient.h>
#include <M5StickCPlus.h>

// WiFi credentials
const char* ssid = "KATE_ASUS";
const char* password = "moreno1010";

// Django backend API URL
const char* backendUrl = "http://192.168.1.127:8000/";

void setup() {
  M5.begin();
  M5.Lcd.setRotation(1); // Adjust screen rotation if needed
  M5.Lcd.fillScreen(BLACK); // Fill screen with black color
  M5.Lcd.setCursor(20, 20); // Set cursor position
  M5.Lcd.setTextColor(WHITE); // Set text color to white
  M5.Lcd.setTextSize(2); // Set text size
  M5.Lcd.print("Hello, World!"); // Display text

  Serial.begin(115200);
  delay(4000);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Example data to send from M5StickC to Django backend
  String dataToSend = "Hello from M5StickC!";

  // Send data to Django backend
  sendToBackend(dataToSend);
  
  // Check for incoming data from Django backend
  checkForIncomingData();
  
  delay(5000); // Wait before sending/receiving data again
}

void sendToBackend(String data) {
  HTTPClient http;
  // Convert backendUrl to String object
  String url = backendUrl;
  // Concatenate the strings
  url.concat("send_data/");
  http.begin(url);
  // http.begin(backendUrl + "send_data/");
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(data);
  if (httpResponseCode > 0) {
    Serial.print("Data sent to backend. HTTP Response code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("Error sending data to backend. Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

void checkForIncomingData() {
  HTTPClient http;
  // Convert backendUrl to String object
  String url = backendUrl;
  // Concatenate the strings
  url.concat("get_data/");
  http.begin(url);
  // http.begin(backendUrl + "get_data/");
  
  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Received data from backend: " + response);
    // Process the received data as needed
  } else {
    Serial.print("Error checking for incoming data from backend. Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}
