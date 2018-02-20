#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUDP.h>
#include <ArduinoOTA.h>

const char* ssid = "Masha";
const char* password = "‎‎23062005";

//const char* ssid = "demonukraine";
//const char* password = "‎25801234d";


void restart() {
  ESP.reset();
}

void setup() {
  Serial.begin(115200);
//  Serial.setDebugOutput(true);
  Serial.print("Initializing board\n");
  
//  Serial.print("Scan start ... ");
//  int n = WiFi.scanNetworks();
//  Serial.print(n);
//  Serial.println(" network(s) found");
//  int encryption_type;
//  for (int i = 0; i < n; i++)
//  {
//      Serial.print(i + 1);
//      Serial.print(": ");
//      Serial.print(WiFi.SSID(i));
//      Serial.print(" (");
//      Serial.print(WiFi.RSSI(i));
//      Serial.print(") (");
//      
//      encryption_type = WiFi.encryptionType(i);
//      if(encryption_type == ENC_TYPE_WEP) Serial.print("WEP");
//      else if(encryption_type == ENC_TYPE_TKIP) Serial.print("TKIP");
//      else if(encryption_type == ENC_TYPE_CCMP) Serial.print("CCMP");
//      else if(encryption_type == ENC_TYPE_NONE) Serial.print("NONE");
//      else if(encryption_type == ENC_TYPE_AUTO) Serial.print("AUTO");
//      Serial.print(") ");
//
//      Serial.print("channel=");
//      Serial.println(WiFi.channel(i));
//      
//      delay(10);
//  }
//  Serial.println();

  int status;
  int mode_status = -1;
  do {

    if(mode_status == -1) {
      mode_status = WiFi.mode(WIFI_STA);
      if(mode_status) {
        Serial.println("WiFi mode succesfully changed to WIFI_STA");
      } else {
        Serial.println("Error at setting up WiFi mode");
      }
    }
    
    Serial.print("Trying to connect to wifi");
    WiFi.begin(ssid, password, 1);
 
    do {
      status = WiFi.status();
      Serial.print(".");
      delay(500);
    } while (status != WL_CONNECTED && status != WL_CONNECT_FAILED);
    Serial.println();
  
    if(status == WL_CONNECTED) {
      Serial.println("Succesfully connected!");
    } else if(status == WL_CONNECT_FAILED) {
      Serial.println("Connect failed");
      delay(500);
      ESP.restart();
    } else {
      Serial.print("Got unknown status: ");
      Serial.println(status);
    }
  } while(status != WL_CONNECTED);

  ArduinoOTA.setHostname("dea-esp8266");
  Serial.println("Starting OTA protocol");
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();  
  
}