#include <ESP8266WiFi.h>
#include <Servo.h>

// --- KONFIGURACJA SIECI ---
const char* ssid = "WIFI SSID";
const char* password = "WIFI PASSWORD";

Servo mojeSerwo;
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  delay(10);


  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

 
  mojeSerwo.attach(4); 
  mojeSerwo.write(90); 


  Serial.print("Łączenie z siecią: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }


  server.begin();
  Serial.println("");
  Serial.println("Felix połączony z WiFi!");
  Serial.print("Adres IP modułu: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  WiFiClient client = server.available();
  if (!client) return;


  String request = client.readStringUntil('\r');
  Serial.println("Otrzymano zapytanie: " + request);

 
  if (request.indexOf("/ON") != -1) {
    digitalWrite(LED_BUILTIN, HIGH);   
    mojeSerwo.write(180);             
    delay(800);                       
    mojeSerwo.write(90);    
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);            
  }
  

  if (request.indexOf("/OFF") != -1) {
    digitalWrite(LED_BUILTIN, HIGH);  
    mojeSerwo.write(0);             
    delay(800);                       
    mojeSerwo.write(90); 
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);            
  }
  
 
  client.flush();
}