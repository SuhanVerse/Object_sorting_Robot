#include <Servo.h>
#include <SoftwareSerial.h>

// --- Stepper Pins ---
const int X_STEP_PIN = 2;
const int X_DIR_PIN  = 5;
const int ENABLE_PIN = 8;
const int STEP_DELAY_US = 1200; 

// --- Servo & Sensor Pins ---
const int SERVO_PIN = 9;      
const int IR_START_PIN = A1;  
const int IR_CAMERA_PIN = A2; 

// --- UART Communication ---
SoftwareSerial espSerial(A0, A3); // RX, TX

Servo diverterServo;

// --- Servo Angles ---
const int angleBinA = 0;
const int angleBinB = 50;
const int angleBinC = 140;
const int angleReject = 90; 

enum SystemState { IDLE, MOVING_TO_CAM, SCANNING, DISPATCHING };
SystemState currentState = IDLE;

unsigned long stateTimer = 0;
const unsigned long scanTimeout = 3000;    
const unsigned long dispatchTime = 4000;   

void setup() {
  Serial.begin(115200);
  espSerial.begin(115200);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  
  pinMode(IR_START_PIN, INPUT);
  pinMode(IR_CAMERA_PIN, INPUT);

  digitalWrite(X_DIR_PIN, HIGH); 
  digitalWrite(ENABLE_PIN, HIGH); // Stepper OFF

  diverterServo.attach(SERVO_PIN);
  diverterServo.write(angleBinC); 

  Serial.println("System Ready. Waiting for object...");
}

void stepMotor() {
  digitalWrite(X_STEP_PIN, HIGH);
  delayMicroseconds(STEP_DELAY_US);
  digitalWrite(X_STEP_PIN, LOW);
  delayMicroseconds(STEP_DELAY_US);
}

void loop() {
  int startDetected = digitalRead(IR_START_PIN);
  int camDetected = digitalRead(IR_CAMERA_PIN);
  unsigned long currentMillis = millis();

  switch (currentState) {
    
    case IDLE:
      digitalWrite(ENABLE_PIN, HIGH); 
      
      if (startDetected == LOW) {
        digitalWrite(ENABLE_PIN, LOW); 
        currentState = MOVING_TO_CAM;
        delay(500); 
      }
      break;

    case MOVING_TO_CAM:
      stepMotor(); 
      
      if (camDetected == LOW) {
        currentState = SCANNING;
        stateTimer = currentMillis;
        
        // --- NEW: Ask ESP32 for a decision ---
        espSerial.print('?'); 
      }
      break;

    case SCANNING:
      if (espSerial.available()) {
        char aiCommand = espSerial.read();
        
        if (aiCommand == 'A') diverterServo.write(angleBinA);
        else if (aiCommand == 'B') diverterServo.write(angleBinB);
        else if (aiCommand == 'C') diverterServo.write(angleBinC);
        
        delay(600); // Wait for servo to move
        currentState = DISPATCHING;
        stateTimer = currentMillis;
      } 
      else if (currentMillis - stateTimer > scanTimeout) {
        diverterServo.write(angleReject); 
        delay(600);
        currentState = DISPATCHING;
        stateTimer = currentMillis;
      }
      break;

    case DISPATCHING:
      stepMotor(); 
      
      if (currentMillis - stateTimer > dispatchTime) {
        diverterServo.write(angleBinC); // Reset servo
        currentState = IDLE;
      }
      break;
  }
}