#include "config.h"

bool aButtonState;
bool bButtonState;

void setup() {
  pinMode(A_INPUT, INPUT_PULLUP);
  pinMode(B_INPUT, INPUT_PULLUP);

  pinMode(A_OUTPUT, OUTPUT);
  pinMode(B_OUTPUT, OUTPUT);

  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {
      case 'a':
        engage(A_OUTPUT, SHORT_ENGAGE_MS);
        break;
      case 'A':
        engage(A_OUTPUT, LONG_ENGAGE_MS);
        break;
      case 'b':
        engage(B_OUTPUT, SHORT_ENGAGE_MS);
        break;
      case 'B':
        engage(B_OUTPUT, LONG_ENGAGE_MS);
        break;
      default:
        // Do nothing, just ignore
    }
  }

  bool button;
  // Checking A button
  button = digitalRead(A_INPUT);
  if (button != aButtonState) {
    // Since we have pullup, LOW means button is pressed
    if (button == LOW) {
      engage(A_OUTPUT, LONG_ENGAGE_MS);
    }
    aButtonState = button;
  }
  button = digitalRead(B_INPUT);
  if (button != bButtonState) {
    // Since we have pullup, LOW means button is pressed
    if (button == LOW) {
      engage(B_OUTPUT, LONG_ENGAGE_MS);
    }
    bButtonState = button;
  }
}

void engage(int pin, unsigned int length) {
  digitalWrite(pin, HIGH);
  delay(length);
  digitalWrite(pin, LOW);
}
