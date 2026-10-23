const int X_STEP_PIN = 2;
const int X_DIR_PIN  = 5;
const int ENABLE_PIN = 8;

const int STEP_DELAY_US = 1200; // bigger = slower, safer
const int STEPS_TO_MOVE = 800;  // full-step: 800 = 4 rotations

void setup() {
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  digitalWrite(ENABLE_PIN, LOW); // A4988 enable is active LOW
}

void moveStepper(bool direction, int steps) {
  digitalWrite(X_DIR_PIN, direction);
  delay(100);

  for (int i = 0; i < steps; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
}

void loop() {
  moveStepper(HIGH, STEPS_TO_MOVE);
  delay(1000);

  moveStepper(LOW, STEPS_TO_MOVE);
  delay(1000);
}
