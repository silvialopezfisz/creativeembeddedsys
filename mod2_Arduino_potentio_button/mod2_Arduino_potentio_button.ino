// This file is simply the Arduino IDE code I flashed on my esp32 to read in the potentiometer and button values
// through the serial monitor
const uint8_t BUTTON_PIN = 33;

void setup() {
  Serial.begin(115200); // Start serial communication at 115200 baud rate
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  int potValue = analogRead(25); // Read the analog value from pin 25
  int buttonValue = digitalRead(BUTTON_PIN); // Read the digital value from the button pin

  // Format: "potValue,buttonValue"
  Serial.println(String(potValue) + "," + String(buttonValue));

  delay(100); // Wait for 100 milliseconds
}


// OLD CODE IN CASE STUFF BREAKS
// const uint8_t BUTTON_PIN = 33;

// void setup() {
//   Serial.begin(115200); // Start serial communication at 115200 baud rate
//   pinMode(BUTTON_PIN, INPUT_PULLUP);

// }

// void loop() {
//   int potValue = analogRead(25); // Read the analog value from pin 34
//   touch_value_t buttonValue = touchRead(BUTTON_PIN);

//   //format : "potValue,buttonValue"
//   Serial.println(String(potValue) + "," + String(buttonValue));

//   delay(100); // Wait for 100 milliseconds
// }