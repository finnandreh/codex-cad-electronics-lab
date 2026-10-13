// Designed with OpenAI Codex for Finn Andre. Unflashed / not bench-tested.
// Arduino ESP32 core + PubSubClient 2.8 + ArduinoJson 7.
// Separate authenticated LAN test broker required; this is NOT the loopback simulator.
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

constexpr uint8_t DATA_PIN=23,CLOCK_PIN=18,STROBE_PIN=19,BOARD_ADDRESS=5;
constexpr char COMMAND[]="codex/address-led/set";
constexpr char STATE[]="codex/address-led/state/5";
WiFiClientSecure transport;
PubSubClient mqtt(transport);
uint8_t storedMask=0;
uint32_t lastSeq=0,nextConnect=0;

void writeBoard(uint8_t address,uint8_t pattern){
  digitalWrite(STROBE_PIN,HIGH);
  uint16_t frame=(uint16_t(address)<<8)|pattern;
  for(int bit=15;bit>=0;--bit){
    digitalWrite(CLOCK_PIN,LOW);
    digitalWrite(DATA_PIN,(frame>>bit)&1);
    delayMicroseconds(10);
    digitalWrite(CLOCK_PIN,HIGH);
    delayMicroseconds(10);
    digitalWrite(CLOCK_PIN,LOW);
  }
  delayMicroseconds(100);
  digitalWrite(STROBE_PIN,LOW);
  delayMicroseconds(100);
  digitalWrite(STROBE_PIN,HIGH);
  delayMicroseconds(100);
}
void publishState(uint32_t seq,const char* status,uint8_t received){
  JsonDocument d;
  d["address"]=BOARD_ADDRESS;d["mask"]=storedMask;d["seq"]=seq;
  d["status"]=status;d["received_address"]=received;d["simulated"]=false;
  d["evidence"]="controller_sent_frame; physical outputs not sensed";
  char message[240];serializeJson(d,message,sizeof(message));mqtt.publish(STATE,message,true);
}
void onMessage(char* topic,byte* payload,unsigned int length){
  if(strcmp(topic,COMMAND)||length>240)return;
  JsonDocument d;
  if(deserializeJson(d,payload,length,DeserializationOption::NestingLimit(2)))return;
  if(!d.is<JsonObject>()||d.size()!=4||!d["version"].is<int>()||d["version"]!=1||
     !d["address"].is<int>()||!d["mask"].is<int>()||!d["seq"].is<uint32_t>())return;
  int address=d["address"],mask=d["mask"];uint32_t seq=d["seq"];
  if(address<0||address>15||mask<0||mask>255||seq==0||seq<=lastSeq)return;
  lastSeq=seq;
  writeBoard(address,mask); // Hardware comparator prevents an unmatched latch write.
  if(address==BOARD_ADDRESS)storedMask=mask;
  publishState(seq,address==BOARD_ADDRESS?"frame_sent":"address_mismatch",address);
}
void setup(){
  // Set output latches before enabling drivers; external pull-downs still require bench validation.
  digitalWrite(STROBE_PIN,HIGH);digitalWrite(CLOCK_PIN,LOW);digitalWrite(DATA_PIN,LOW);
  pinMode(STROBE_PIN,OUTPUT);pinMode(CLOCK_PIN,OUTPUT);pinMode(DATA_PIN,OUTPUT);
  writeBoard(BOARD_ADDRESS,0);
  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);
  transport.setCACert(MQTT_CA_CERT); // No insecure TLS fallback.
  mqtt.setServer(MQTT_HOST,MQTT_PORT);mqtt.setCallback(onMessage);mqtt.setBufferSize(512);
}
void loop(){
  if(WiFi.status()!=WL_CONNECTED){delay(10);return;}
  if(!mqtt.connected()){
    if(int32_t(millis()-nextConnect)>=0){
      nextConnect=millis()+5000;
      if(mqtt.connect("codex-address-led-physical",MQTT_USER,MQTT_PASSWORD))mqtt.subscribe(COMMAND,1);
    }
  }else mqtt.loop();
  delay(1);
}
