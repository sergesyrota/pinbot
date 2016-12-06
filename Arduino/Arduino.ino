#include "config.h"
#include "DigitalWriteFast.h"

bool aButtonState;
bool bButtonState;

void setup() {
  pinMode(A_INPUT, INPUT_PULLUP);
  pinMode(B_INPUT, INPUT_PULLUP);

  pinModeFast(A_OUTPUT, OUTPUT);
  pinModeFast(B_OUTPUT, OUTPUT);

  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 1) {
    // Protocol: 1st byte: a or b, for one of the outputs.
    //           2nd byte: how long to hold the button (in 10 ms increments, e.g. 3 = 30ms)
    char c = Serial.read();
    unsigned int delay = Serial.read() * 10;
    switch (c) {
      case 'a': // Fall through on purpose
      case 'A':
        engage(A_OUTPUT, delay);
        break;
      case 'b': // Fall through on purpose
      case 'B':
        engage(B_OUTPUT, delay);
        break;
      default:
        // Do nothing, just ignore
        break;
    }
      Serial.write(c);
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
  digitalWriteFast(pin, HIGH);
  delay(length);
  digitalWriteFast(pin, LOW);
}
