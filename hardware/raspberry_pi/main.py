#!/home/will/main/venv/bin/python

import time
import math
import socket
import struct
import RPi.GPIO as GPIO
#import pigpio
from adafruit_servokit import ServoKit

PWM_FREQUENCY = 10000  # 10kHz frequency for PWM
SPEED = [1, 5, 15, 25, 50, 99]
speed_mode = 0

INHIBIT_MOTION = 1

AXIS_TILT = 3
AXIS_PAN = 2
AXIS_FB = 1
AXIS_LR = 0

# AXIS_TILT = 1
# AXIS_PAN = 0
# AXIS_FB = 3
# AXIS_LR = 2

def clamp(value, min_value, max_value):
    """Clamp the value between min_value and max_value."""
    if(abs(value) < 0.001):
        value = 0
    return max(min(value, max_value), min_value)

def set_motors(L_mot,R_mot):
    if(abs(L_mot) > 0.01 or abs(R_mot) > 0.01):
        if(L_mot <= 0 and R_mot <= 0):
            set_digital_outputs([0, 1, 1, 0])
        elif(L_mot <= 0 and R_mot > 0):
            #set_digital_outputs([1, 0, 1, 0])
            set_digital_outputs([0, 1, 0, 1])
        elif(L_mot > 0 and R_mot <= 0):
            #set_digital_outputs([0, 1, 0, 1])
            set_digital_outputs([1, 0, 1, 0])
        elif(L_mot > 0 and R_mot > 0):
            set_digital_outputs([1, 0, 0, 1])
        pwm_l = abs(L_mot)*abs(L_mot)*SPEED[speed_mode]
        pwm_r = abs(R_mot)*abs(R_mot)*SPEED[speed_mode]
        set_pwm(13, pwm_r)
        set_pwm(19, pwm_l)
#         print(f"L_mot: {pwm_l}  R_mot: {pwm_r}")
#         set_pwm(13, 0)  
#         set_pwm(19, 0)
    else:
        set_pwm(13, 0)  
        set_pwm(19, 0)
        set_digital_outputs([0, 0, 0, 0])

# Servo
kit = ServoKit(channels=16)
pan = 120; #default straight is 120
tilt = 100; #defalt level is 100
pan_default = 120;
tilt_default = 100;

# Configuration
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005

# Calibration
zero_tol = 0.1
axis_dead = 0.01
straight_ln = 1

# Setup for digital outputs
DIGITAL_OUTPUTS = [24, 25, 22, 23]

# Setup for PWM outputs
PWM_OUTPUTS = {
    13: None,  # GPIO 13
    19: None   # GPIO 19
}

ENCODER_L_GPIO_PIN = 17
ENCODER_R_GPIO_PIN = 18

pulse_count_R = 0
pulse_count_L = 0

def encode_L_callback(channel):
    global pulse_count_L
    pulse_count_L += 1
    
def encode_R_callback(channel):
    global pulse_count_R
    pulse_count_R += 1
    
def setup():
    # Set the GPIO mode
    GPIO.setmode(GPIO.BCM)
    
    # Setup digital output pins
    for pin in DIGITAL_OUTPUTS:
        GPIO.setup(pin, GPIO.OUT)
    
    # Setup PWM pins
    for pin in PWM_OUTPUTS:
        GPIO.setup(pin, GPIO.OUT)
        PWM_OUTPUTS[pin] = GPIO.PWM(pin, PWM_FREQUENCY)
        PWM_OUTPUTS[pin].start(0)  # Start PWM with 0% duty cycle
    # Encoder Pin
    GPIO.setup(ENCODER_L_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(ENCODER_R_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.add_event_detect(ENCODER_L_GPIO_PIN, GPIO.RISING, callback=encode_L_callback, bouncetime=1)
    #GPIO.add_event_detect(ENCODER_R_GPIO_PIN, GPIO.RISING, callback=encode_R_callback, bouncetime=1)

def set_digital_outputs(values):
    """Set digital output pins with a list of HIGH or LOW values"""
    for pin, value in zip(DIGITAL_OUTPUTS, values):
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
        

def set_pwm(pin, duty_cycle):
    """Set PWM duty cycle for a specific pin (0 to 100%)"""
    if pin in PWM_OUTPUTS:
        PWM_OUTPUTS[pin].ChangeDutyCycle(duty_cycle)




setup()

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening on port {UDP_PORT}...")


try:
    while True:
        # Receive data from the network
        data, addr = sock.recvfrom(4*4 + 2)  # Expecting 4 floats and 4 bytes
        if len(data) == 18:  # 4 floats (16 bytes) + 4 bytes = 20 bytes
            # Unpack the data
            #unpacked_data = struct.unpack('ffffBBBB', data)
            unpacked_data = struct.unpack('ffffH', data)
            axis_values = unpacked_data[:4]
            button_values = unpacked_data[4]
            
            #servos
            if(button_values & 1):
                tilt = tilt_default
                pan = pan_default
            
            if(button_values & 64):
                speed_mode = 5
            if(button_values & 128):
                speed_mode = 4
            if(button_values & 256):
                speed_mode = 3             
            if(button_values & 512):
                speed_mode = 2
            if(button_values & 1024):
                speed_mode = 1
            if(button_values & 2048):
                speed_mode = 0                
            
            if(abs(axis_values[AXIS_PAN]) > axis_dead):
                pan = pan - 0.8*axis_values[AXIS_PAN]
                if(pan > 179):
                    pan = 179
                if(pan < 1):
                    pan = 1
            if(abs(axis_values[AXIS_TILT]) > axis_dead):
                tilt = tilt - 0.8*axis_values[AXIS_TILT]
                if(tilt > 179):
                    tilt = 179
                if(tilt < 1):
                    tilt = 1
                    
            kit.servo[15].angle = pan
            kit.servo[14].angle = tilt
            
            # Motors
            L_motor = 0
            R_motor = 0
            
            #if(abs(axis_values[1]) > axis_dead or axis_values[0] > axis_dead):
            L_motor = -(axis_values[AXIS_FB] - axis_values[AXIS_LR])
            R_motor = -(axis_values[AXIS_FB] + axis_values[AXIS_LR])

            # Clamp motor outputs to -1 to 1
            L_motor = clamp(L_motor, -1, 1)
            R_motor = clamp(R_motor, -1, 1)
            set_motors(L_motor,R_motor)
            
            
            # Debug print
            #print(f"Received axis values: {axis_values}")
            #print(f"Button values: {button_values}")
            #print(f"L_mot: {L_motor}  R_mot: {R_motor}")
            #print(f"Pulse count R: {pulse_count_R} Pulse count L: {pulse_count_L}")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Stop all PWM outputs
    for pin in PWM_OUTPUTS:
        PWM_OUTPUTS[pin].stop()
    GPIO.cleanup()

    sock.close()

