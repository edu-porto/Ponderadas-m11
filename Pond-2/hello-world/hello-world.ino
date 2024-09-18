// ledPin refers to ESP32-CAM GPIO 4 (flashlight)
const int ledPin = 4;

void setup() {
  pinMode(ledPin, OUTPUT);  // Initialize the LED pin as an output.
}

void dot() {
  digitalWrite(ledPin, HIGH);
  delay(200);  // 200 ms on for a dot.
  digitalWrite(ledPin, LOW);
  delay(200);  // 200 ms off between dots/dashes.
}

void dash() {
  digitalWrite(ledPin, HIGH);
  delay(600);  // 600 ms on for a dash.
  digitalWrite(ledPin, LOW);
  delay(200);  // 200 ms off between dots/dashes.
}

void letterSpace() {
  delay(600);  // 600 ms off between letters.
}

void wordSpace() {
  delay(1400);  // 1400 ms off between words.
}

void blinkMorse(const char* morseCode) {
  for (int i = 0; morseCode[i] != '\0'; i++) {
    if (morseCode[i] == '.') {
      dot();
    } else if (morseCode[i] == '-') {
      dash();
    }
    if (morseCode[i + 1] != '\0') {  // Don't add space after the last character.
      letterSpace();
    }
  }
}

void loop() {
  blinkMorse(".... . .-.. .-.. ---");  // "HELLO"
  wordSpace();
  blinkMorse(".-- --- .-. .-.. -..");  // "WORLD"
  delay(3000);  // Wait 3 seconds before repeating.
}