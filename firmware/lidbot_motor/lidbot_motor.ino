// lid-bot motor firmware: ESP32 + L298N, two DC motors (differential drive)
//
// Protocol (from the PC over USB serial, 115200 baud):
//   one line per command: "<left> <right>\n"
//   each value is -255..255 (negative = backward, 0 = stop)
//   example: "150 -150" spins in place
//
// Safety: if no command arrives for TIMEOUT_MS, both motors stop.
// That way the car stops if ROS crashes or the cable gets pulled.

// ---- PIN MAP: CHANGE THESE to match how your ESP32 is wired to the L298N ----
// Trace each wire from the L298N header (ENA, IN1, IN2, IN3, IN4, ENB)
// back to the ESP32 and write the GPIO number here.
const int ENA = 14;  // left motor speed (PWM)
const int IN1 = 27;  // left motor direction A
const int IN2 = 26;  // left motor direction B
const int ENB = 32;  // right motor speed (PWM)
const int IN3 = 25;  // right motor direction A
const int IN4 = 33;  // right motor direction B

// If a wheel spins the wrong way, flip its flag instead of rewiring.
const bool INVERT_LEFT = false;
const bool INVERT_RIGHT = false;

const unsigned long TIMEOUT_MS = 500;

String buf;
unsigned long lastCmd = 0;

void setMotor(int en, int a, int b, int speed, bool invert) {
  if (invert) speed = -speed;
  speed = constrain(speed, -255, 255);
  digitalWrite(a, speed > 0 ? HIGH : LOW);
  digitalWrite(b, speed < 0 ? HIGH : LOW);
  analogWrite(en, abs(speed));
}

void stopAll() {
  setMotor(ENA, IN1, IN2, 0, false);
  setMotor(ENB, IN3, IN4, 0, false);
}

void handleLine(const String &line) {
  int l, r;
  if (sscanf(line.c_str(), "%d %d", &l, &r) == 2) {
    setMotor(ENA, IN1, IN2, l, INVERT_LEFT);
    setMotor(ENB, IN3, IN4, r, INVERT_RIGHT);
    lastCmd = millis();
  }
}

void setup() {
  Serial.begin(115200);
  int pins[] = {ENA, IN1, IN2, ENB, IN3, IN4};
  for (int p : pins) pinMode(p, OUTPUT);
  stopAll();
  Serial.println("lidbot ready");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(buf);
      buf = "";
    } else if (c != '\r') {
      buf += c;
      if (buf.length() > 32) buf = "";  // junk guard
    }
  }
  if (millis() - lastCmd > TIMEOUT_MS) stopAll();
}
