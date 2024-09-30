// Include the Wire library for I2C
#include <Wire.h>
#include <Servo.h>
Servo Servo1;
Servo Servo2;

//Set pins and initialize servo values; 
const int ledPin = 13;
int servoVal1=90;
int servoVal2=90;
int servopin=2;
int servopin2=3;


void setup() {
  Serial.begin(9600);
  Servo1.attach(servopin);
  Servo2.attach(servopin2);
  // Join I2C bus as slave with address 8
  Wire.begin(0x8);
  // Call receiveEvent when data received                
  Wire.onReceive(receiveEvent);
}
 

// Function that executes whenever data is received from the Raspberry Pi
void receiveEvent(int howMany) {
  while (Wire.available()) {
    int received = Wire.read(); // Read the incoming byte

    // Split the received byte into x and y values
    int y = received / 10;  // Extract y value from the tens place
    int x = received % 10;  // Extract x value from the ones place

    // Adjust servoVal1 (horizontal movement) based on x value
    if (x >= 5 && x <= 9 && servoVal1 <= 170) {
      servoVal1 += (x - 4);  // Add 1-5 based on x value
    } else if (x >= 0 && x <= 4 && servoVal1 > 10) {
      servoVal1 -= (5 - x);  // Subtract 1-5 based on x value
    }

    // Adjust servoVal2 (vertical movement) based on y value
    if (y >= 5 && y <= 9 && servoVal2 >= 40) {
      servoVal2 -= (y - 4);  // Subtract 1-5 based on y value
    } else if (y >= 0 && y <= 4 && servoVal2 <= 130) {
      servoVal2 += (5 - y);  // Add 1-5 based on y value
    }
  }
}

void loop() {
  // Update servo positions
  Servo1.write(servoVal1);
  Servo2.write(servoVal2);
  
  delay(50);  // Small delay to smooth out movements
}