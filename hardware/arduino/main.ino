#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Arduino.h>
#include <stdint.h>

// Define pin connections
#define IN1_PIN 7
#define IN2_PIN 8
#define IN3_PIN 11
#define IN4_PIN 12
#define ENA1_PIN 9
#define ENA2_PIN 10

#define ENCL_PIN 2
#define ENCR_PIN 3

#define SERVOMIN  150
#define SERVOMAX  600
#define PAN_SERVO 15
#define TILT_SERVO 14
#define PAN_HOME 420
#define TILT_HOME 450

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

volatile int encode_R = 0; 
volatile int encode_L = 0;

bool new_data;
byte data[4];
uint32_t cntrl[4];
bool cntrl_b[4];
byte cntrl_byt[8];

void setup() {

  Serial.begin(9600);
  //Serial.println("Starting PCA9685...");
  pwm.begin();
  pwm.setPWMFreq(50);

  // Set pins as outputs
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(IN3_PIN, OUTPUT);
  pinMode(IN4_PIN, OUTPUT);

  pinMode(ENA1_PIN, OUTPUT);
  pinMode(ENA2_PIN, OUTPUT);

  pinMode(ENCL_PIN, INPUT_PULLUP);
  pinMode(ENCR_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENCL_PIN), handleInterrupt2, FALLING);
  attachInterrupt(digitalPinToInterrupt(ENCR_PIN), handleInterrupt3, FALLING);
  
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, LOW);
  digitalWrite(IN3_PIN, LOW);
  digitalWrite(IN4_PIN, LOW);
  digitalWrite(ENA1_PIN, LOW);
  digitalWrite(ENA2_PIN, LOW);
  pwm.setPWM(PAN_SERVO, 0, PAN_HOME-50);
  delay(500);
  pwm.setPWM(PAN_SERVO, 0, PAN_HOME);
  pwm.setPWM(TILT_SERVO, 0, TILT_HOME);
  delay(500);
  
}

void loop() {

  // send encoder data over serial communication
  Serial.print(encode_L);
  Serial.print(encode_R);

  //baby button board
  if (Serial.available() >= 18) {
    uint8_t check;
    uint8_t byte_data;
    uint8_t buffer[17];
    while(1){
      check = Serial.read();
      if(check == 0xFF){
        break;
      }
    }
    for (int i = 0; i < 17; i++) {
      buffer[i] = Serial.read();
    }

    cntrl[0] = (uint32_t)buffer[0] << 24 | (uint32_t)buffer[1] << 16 | (uint32_t)buffer[2] << 8 | (uint32_t)buffer[3];
    cntrl[1] = (uint32_t)buffer[4] << 24 | (uint32_t)buffer[5] << 16 | (uint32_t)buffer[6] << 8 | (uint32_t)buffer[7];
    cntrl[2] = (uint32_t)buffer[8] << 24 | (uint32_t)buffer[9] << 16 | (uint32_t)buffer[10] << 8 | (uint32_t)buffer[11];
    cntrl[3] = (uint32_t)buffer[12] << 24 | (uint32_t)buffer[13] << 16 | (uint32_t)buffer[14] << 8 | (uint32_t)buffer[15];
    //Serial.write(buffer, 17);
    byte_data = buffer[16];
    for (int i = 0; i < 4; i++) {
      cntrl_b[i] = byte_data & (1 << i);
    }
  }


  pwm.setPWM(PAN_SERVO, 0, cntrl[0]);
  pwm.setPWM(TILT_SERVO, 0, cntrl[1]);

  analogWrite(ENA1_PIN, cntrl[2]);
  analogWrite(ENA2_PIN, cntrl[3]);

  digitalWrite(IN1_PIN, cntrl_b[0]);
  digitalWrite(IN2_PIN, cntrl_b[1]);
  digitalWrite(IN3_PIN, cntrl_b[2]);
  digitalWrite(IN4_PIN, cntrl_b[3]);
}

void test_animation(){
  int dt = 2;
    for(int i = PAN_HOME; i < SERVOMAX; i++){
      pwm.setPWM(PAN_SERVO, 0, i);
      delay(dt);
    }
    for(int i = SERVOMAX; i > SERVOMIN; i--){
      pwm.setPWM(PAN_SERVO, 0, i);
      delay(dt);
    }
    for(int i = SERVOMIN; i < PAN_HOME; i++){
      pwm.setPWM(PAN_SERVO, 0, i);
      delay(dt);
    }
    pwm.setPWM(PAN_SERVO, 0, PAN_HOME);
}


void handleInterrupt2() {
  encode_R++;
  new_data = true;
}

// Interrupt service routine for pin 3
void handleInterrupt3() {
  encode_L++;
  new_data = true;
}
