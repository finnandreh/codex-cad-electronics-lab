#pragma once
// Copy to secrets.h privately; never publish real credentials.
constexpr char WIFI_SSID[]="YOUR_TEST_WIFI";
constexpr char WIFI_PASSWORD[]="YOUR_TEST_WIFI_PASSWORD";
constexpr char MQTT_HOST[]="YOUR_AUTHENTICATED_TEST_BROKER_HOST";
constexpr uint16_t MQTT_PORT=8883;
constexpr char MQTT_USER[]="YOUR_DEVICE_ACCOUNT";
constexpr char MQTT_PASSWORD[]="YOUR_DEVICE_PASSWORD";
constexpr char MQTT_CA_CERT[]=R"PEM(
-----BEGIN CERTIFICATE-----
YOUR_BROKER_CA_CERTIFICATE
-----END CERTIFICATE-----
)PEM";
