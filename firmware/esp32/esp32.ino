#include <ESP32Servo.h>

Servo tiltServo;
Servo panServo;

const int tiltPin = 13;
const int panPin  = 19;

int panAngle  = 90;
int tiltAngle = 40;

void setup() {
  Serial.begin(115200);

  tiltServo.attach(tiltPin, 500, 2400);
  panServo.attach(panPin, 500, 2400);

  tiltServo.write(tiltAngle);
  panServo.write(panAngle);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("HOME")) {
      int comma1 = cmd.indexOf(',');
      int comma2 = cmd.indexOf(',', comma1 + 1);

      if (comma1 > 0 && comma2 > comma1) {
        int panHome = cmd.substring(comma1 + 1, comma2).toInt();
        int tiltHome = cmd.substring(comma2 + 1).toInt();

        panAngle = constrain(panHome, 0, 180);
        tiltAngle = constrain(tiltHome, 0, 90);

        panServo.write(panAngle);
        tiltServo.write(tiltAngle);

        Serial.print("HOME -> Pan = ");
        Serial.print(panAngle);
        Serial.print(" | Tilt = ");
        Serial.println(tiltAngle);
      }
    }

    else if (cmd.startsWith("CTRL")) {
      int comma1 = cmd.indexOf(',');
      int comma2 = cmd.indexOf(',', comma1 + 1);

      if (comma1 > 0 && comma2 > comma1) {
        float ux = cmd.substring(comma1 + 1, comma2).toFloat();
        float uy = cmd.substring(comma2 + 1).toFloat();

        if (ux > 4) ux = 4;
        if (ux < -4) ux = -4;

        if (uy > 3) uy = 3;
        if (uy < -3) uy = -3;

        panAngle -= (int)ux;
        tiltAngle -= (int)uy;

        panAngle = constrain(panAngle, 0, 180);
        tiltAngle = constrain(tiltAngle, 30, 60);

        panServo.write(panAngle);
        tiltServo.write(tiltAngle);

        Serial.print("Pan = ");
        Serial.print(panAngle);
        Serial.print(" | Tilt = ");
        Serial.println(tiltAngle);
      }
    }
  }
}