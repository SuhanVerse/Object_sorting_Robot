#include <Servo.h>

Servo diverterServo;
const int SERVO_PIN = 9; // CHANGE THIS to your exact Arduino servo pin

void setup() {
  Serial.begin(115200);
  diverterServo.attach(SERVO_PIN);
  
  Serial.println("\n--- Servo Calibration Tool ---");
  Serial.println("Type an angle (0 to 180) in the input box and press Enter.");
  
  // Start at an arbitrary safe angle
  diverterServo.write(90); 
  Serial.println("Servo centered at 90 degrees.");
}

void loop() {
  if (Serial.available() > 0) {
    int angle = Serial.parseInt();
    
    // Clear the serial buffer of any newline characters
    while(Serial.read() != -1); 

    if (angle >= 0 && angle <= 180) {
      Serial.print("Moving servo to: ");
      Serial.print(angle);
      Serial.println(" degrees.");
      diverterServo.write(angle);
    } else {
      Serial.println("Invalid input. Enter a number between 0 and 180.");
    }
  }
}