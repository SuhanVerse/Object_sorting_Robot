#include <Servo.h>

// --- CNC Shield V3 / A4988 Pins ---
#define EN_PIN    8  // Stepper Enable (Active LOW - prevents overheating)
#define DIR_PIN   5  // Direction (e.g., X-Axis on CNC Shield)
#define STEP_PIN  2  // Step (e.g., X-Axis on CNC Shield)

// --- Sensor & Servo Pins ---
#define SERVO_PIN 9  // CNC shield servo pin
#define START_IR  A1 // CNC Shield A1 (Hold) pin
#define SCAN_IR   A2 // CNC Shield A2 (Resume) pin

// --- Calibrated Servo Angles ---
const int ANGLE_BIN_A = 45;
const int ANGLE_BIN_B = 135;
const int ANGLE_BIN_C = 180;
const int ANGLE_IDLE  = 180;  // INITIAL/DEFAULT POSITION

Servo diverterServo;

// --- System State Machine ---
enum SystemState { IDLE, MOVING, SCANNING, DISPATCHING };
SystemState currentState = IDLE;

// --- Test Sequence Counter ---
int testSequence = 0; 

void setup() {
  // NOTE: Serial.begin() completely removed for standalone 12V operation.

  pinMode(EN_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  
  pinMode(START_IR, INPUT_PULLUP);
  pinMode(SCAN_IR, INPUT_PULLUP);

  diverterServo.attach(SERVO_PIN);
  
  // Set the initial default position immediately on startup
  diverterServo.write(ANGLE_IDLE);

  // Disable stepper initially to save power and prevent thermal shutdown
  digitalWrite(EN_PIN, HIGH); 
  
  // Set belt direction
  digitalWrite(DIR_PIN, LOW); 
}

void loop() {
  switch (currentState) {
    
    case IDLE:
      // Wait for object at the start of the belt
      // NOTE: If the belt doesn't start, change LOW to HIGH here.
      if (digitalRead(START_IR) == LOW) {
        digitalWrite(EN_PIN, LOW); // Wake up the stepper motor
        delay(10);
        currentState = MOVING;
      }
      break;
      
    case MOVING:
      stepMotor();
      // Stop moving when object hits the camera scan point
      if (digitalRead(SCAN_IR) == LOW) {
        currentState = SCANNING;
      }
      break;

    case SCANNING:
      // Cycle through the angles: 45 -> 135 -> 180 automatically
      if (testSequence == 0) {
        diverterServo.write(ANGLE_BIN_A); // 45
      } 
      else if (testSequence == 1) {
        diverterServo.write(ANGLE_BIN_B); // 135
      } 
      else if (testSequence == 2) {
        diverterServo.write(ANGLE_BIN_C); // 180
      }

      // Increment sequence for the next box
      testSequence++;
      if (testSequence > 2) {
        testSequence = 0; 
      }
      
      delay(600); // Give physical arm time to swing into position
      currentState = DISPATCHING;
      break;

    case DISPATCHING:
      // Run belt forward to push box into bin
      for (int i = 0; i < 3000; i++) { 
        stepMotor();
      }
      
      // Reset arm and put motor to sleep
      diverterServo.write(ANGLE_IDLE); 
      digitalWrite(EN_PIN, HIGH); 
      currentState = IDLE;
      break;
  }
}

// --- Custom Stepper Pulse Function ---
void stepMotor() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(800); 
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(800);
}