#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "iPhone de David";
const char* password = "00000000";
const String serverUrl = "https://api-interface-web.onrender.com/check_badge"; 

#define SS_PIN  5   // GPIO5 -> SDA (SS) du MFRC522
#define RST_PIN 22  // GPIO22 -> RST du MFRC522
MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
    Serial.begin(115200);
    SPI.begin();
    rfid.PCD_Init();
    lcd.init();
    lcd.backlight();
    lcd.print("Initialisation...");  

    Serial.println("Connexion au Wi-Fi...");
    WiFi.begin(ssid, password);
    
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(1000);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnecté au Wi-Fi !");
        lcd.clear();
        lcd.print("Connecté au WiFi");
    } else {
        Serial.println("\nÉchec connexion WiFi !");
        lcd.clear();
        lcd.print("Erreur WiFi !");
        return;
    }

    delay(2000);
    lcd.clear();
    lcd.print("Scannez le badge");
}

void loop() {
    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
        return;
    }

    Serial.println("Carte détectée !");
    
    String badgeUID = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        badgeUID += String(rfid.uid.uidByte[i], HEX);
    }

    Serial.print("Badge UID: ");
    Serial.println(badgeUID);

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi déconnecté !");
        lcd.clear();
        lcd.print("Erreur WiFi !");
        delay(3000);
        return;
    }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"badgeuid\": \"" + badgeUID + "\"}";
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Réponse du serveur : " + response);

        lcd.clear();
        if (response == "access_ok") {
            Serial.println("Accès autorisé !");
            lcd.print("Acces autorise !");
        } else {
            Serial.println("Accès refusé !");
            lcd.print("Acces refuse !");
        }
    } else {
        Serial.print("Erreur HTTP : ");
        Serial.println(httpResponseCode);
        lcd.clear();
        lcd.print("Erreur HTTP !");
    }

    http.end();

    delay(2000);
    lcd.clear();
    lcd.print("Scannez le badge");
}
