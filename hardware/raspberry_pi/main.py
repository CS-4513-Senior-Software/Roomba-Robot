#!/home/will/main/venv/bin/python
import time
import math
import socket
import struct
import serial
from serial import Serial
import pygame
import typing

class DigitalWriteException(Exception):
    pass

SPEED = [1, 2, 3, 4, 5, 6]
speed_mode = 0
mc_inn = [0,0,0,0]

INHIBIT_MOTION = 1

AXIS_TILT = 3
AXIS_PAN = 2
AXIS_FB = 1
AXIS_LR = 0

def digital_write(currInts: list[int], endInts: list[int], bool_byte, easing = True, n_steps = 100):
        if len(currInts) != len(endInts) or len(currInts) != 4:
            raise DigitalWriteException("current and ending lists must both be of length 4")

        if (not easing):
            data = struct.pack('>BIIIIB',0xFF, *endInts, bool_byte)
            ser.write(data)
            return
        
        stepSize0 = (endInts[0] - currInts[0]) / n_steps
        stepSize1 = (endInts[1] - currInts[1]) / n_steps
        stepSize2 = (endInts[2] - currInts[2]) / n_steps
        stepSize3 = (endInts[3] - currInts[3]) / n_steps
        
        stepSizes = [stepSize0, stepSize1, stepSize2, stepSize3]
        
        for i in range(n_steps):
            for j, k in enumerate(currInts):
                stepSize = stepSizes[j]
                currInts[j] += stepSize
                data = struct.pack('>BIIIIB',0xFF, *currInts, bool_byte)
                ser.write(data)
           
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

def clamp(value, min_value, max_value):
    """Clamp the value between min_value and max_value."""
    if(abs(value) < 0.001):
        value = 0
    return max(min(value, max_value), min_value)

def map_range(value, min_old, max_old, min_new, max_new):
    return min_new + (value - min_old) * (max_new - min_new) / (max_old - min_old)


time.sleep(2)  # Give Arduino time to reset

# Servo

pan = 120; #default straight is 120
tilt = 100; #defalt level is 100
pan_default = 120
tilt_default = 100

# Calibration
zero_tol = 0.1
axis_dead = 0.01
straight_ln = 1


pulse_count_L = 0
pygame.init()
# pygame.joystick.init()

# if pygame.joystick.get_count() == 0:
#     print("No joystick connected.")
#     pygame.quit()
#     exit()
    
# joystick = pygame.joystick.Joystick(0)
# joystick.init()
# print(f"Joystick connected: {joystick.get_name()}")


axis_values = [0, 0, 0, 0]
prev_integers = [0, 0, 0, 0]
try:
    while True:
        
        pygame.event.pump()
        
        # axis_values = []
        # for i in range(4):
        #     axis_value = joystick.get_axis(i)
        #     axis_values.append(axis_value)
        
        button_values = 0
        # for i in range(12):
        #     button_value = joystick.get_button(i)  # Returns 0 or 1
        #     button_values = (button_values << 1) | button_value
        #     #button_values.append(button_value)
            
        print(f"axis values: {axis_values}, button values: {button_values}")
            
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
                
            
            
        # Motors
        L_motor = 0
        R_motor = 0
        
        #if(abs(axis_values[1]) > axis_dead or axis_values[0] > axis_dead):
        L_motor = -(axis_values[AXIS_FB] - axis_values[AXIS_LR])
        if(abs(axis_values[AXIS_TILT]) > axis_dead):
            tilt = tilt - 0.8*axis_values[AXIS_TILT]
            if(tilt > 179):
                tilt = 179
            if(tilt < 1):
                tilt = 1
                
            
            
        # Motors
        L_motor = 0
        R_motor = 0
        
        #if(abs(axis_values[1]) > axis_dead or axis_values[0] > axis_dead):
        L_motor = -(axis_values[AXIS_FB] - axis_values[AXIS_LR])
        R_motor = -(axis_values[AXIS_FB] + axis_values[AXIS_LR])
        #print(f"L_motor: {L_motor}  R_motor: {R_motor}")
        # Clamp motor outputs to -1 to 1
        L_motor = clamp(L_motor, -1, 1)
        R_motor = clamp(R_motor, -1, 1)
        print("L_motor " + str(L_motor))
        print("R_motor " + str(R_motor))

        if(abs(L_motor) > 0.01 or abs(R_motor) > 0.01):
            if(L_motor <= 0 and R_motor <= 0): # Reverse
                mc_inn = [1, 0, 1, 0]
            elif(L_motor <= 0 and R_motor > 0):
                mc_inn = [0, 1, 1, 0]
            elif(L_motor > 0 and R_motor <= 0):
                mc_inn = [1, 0, 0, 1]
            elif(L_motor > 0 and R_motor > 0): #Forward
                mc_inn = [0, 1, 0, 1]
            pwm_l = int(((abs(L_motor) * 127.5) + 127.5)/SPEED[speed_mode])
            pwm_r = int(((abs(R_motor) * 127.5) + 127.5)/SPEED[speed_mode])
        else:
            pwm_l = 0
            pwm_r = 0
            mc_inn = [0, 0, 0, 0]

        pan_i = int(map_range(pan, 1, 179, 150, 600))
        tilt_i = int(map_range(tilt, 1, 179, 150, 600))
        integers = [pan_i, tilt_i, pwm_l, pwm_r]
        bool_byte = (mc_inn[0] << 0) | (mc_inn[1] << 1) | (mc_inn[2] << 2) | (mc_inn[3] << 3)
        digital_write(prev_integers, integers, bool_byte, 100)
        prev_integers = integers


        # if (axis_values[0] + 0.01 < 1):
        #     axis_values[0] += 0.01
except KeyboardInterrupt:
    print("Exiting...")
finally:
    print("Exiting...")
