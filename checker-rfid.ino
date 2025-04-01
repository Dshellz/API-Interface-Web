#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Broches pour le module RFID
#define SS_PIN    5
#define RST_PIN   22
MFRC522 mfrc522(SS_PIN, RST_PIN);

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Informations du WiFi
const char* ssid = "RouteurCadeau";
const char* password = "CadeauRouteur";

// URL de l'API
const char* apiUrl = "https://api-interface-web.onrender.com/check_badge";

void setup() {
    Serial.begin(115200);
    SPI.begin();
    mfrc522.PCD_Init();
    lcd.init();
    lcd.backlight();
    lcd.print("Initialisation...");

    // Connexion au WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connexion au WiFi...");
    }
    Serial.println("Connecté au WiFi");
    lcd.clear();
    lcd.print("Connecté au WiFi");
    delay(2000);
    lcd.clear();
    lcd.print("Scannez le badge");
}

void loop() {
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        uid += String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.print("UID du badge : ");
    Serial.println(uid);

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(apiUrl);
        http.addHeader("Content-Type", "application/json");

        String json = "{\"uid\":\"" + uid + "\"}";
        int httpResponseCode = http.POST(json);

        if (httpResponseCode == 200) {
            String response = http.getString();
            if (response == ""access_ok"") {
                lcd.clear();
                lcd.print("Accès autorisé, Bienvenue !");
            } else {
                lcd.clear();
                lcd.print("Accès refusé, Aurevoir !");
            }
        } else {
            lcd.clear();
            lcd.print("Erreur API");
        }
        http.end();
    } else {
        lcd.clear();
        lcd.print("Pas de WiFi");
    }
    delay(3000);
    lcd.clear();
    lcd.print("Scannez le badge");
}