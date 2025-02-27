#!/home/will/main/venv/bin/python
import time
import math
import socket
import struct
import serial
#import pigpio
import pygame


SPEED = [1, 2, 3, 4, 5, 6]
speed_mode = 0
mc_inn = [0,0,0,0]

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

def map_range(value, min_old, max_old, min_new, max_new):
    return min_new + (value - min_old) * (max_new - min_new) / (max_old - min_old)


def send_arduino(serial_ob, axis):
    data = struct.pack('<iiiiB', *integers, bool_byte)
    serial_ob.write(data)


ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Give Arduino time to reset

# Servo

pan = 120; #default straight is 120
tilt = 100; #defalt level is 100
pan_default = 120;
tilt_default = 100;

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
        
            #print(hex_values)
#         if ser.in_waiting > 0:
#             data_s = ser.read(1)
#             value1 = struct.unpack('<B', data_s)
#             print(f"Value 1: {value1}")
        
#         if ser.in_waiting >= 4:
#             data_s = ser.read(4)
#             value1, value2 = struct.unpack('<hh', data_s)
#             print(f"Value 1: {value1}, Value 2: {value2}")
            
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
                #mc_inn = [0, 1, 1, 0]
                mc_inn = [1, 0, 1, 0]
            elif(L_motor <= 0 and R_motor > 0):
                #set_digital_outputs([1, 0, 1, 0])
                #mc_inn = [0, 1, 0, 1]
                mc_inn = [0, 1, 1, 0]
            elif(L_motor > 0 and R_motor <= 0):
                #set_digital_outputs([0, 1, 0, 1])
                #mc_inn = [1, 0, 1, 0]
                mc_inn = [1, 0, 0, 1]
            elif(L_motor > 0 and R_motor > 0): #Forward
                #mc_inn = [1, 0, 0, 1]
                mc_inn = [0, 1, 0, 1]
            #pwm_l = abs(L_motor)*abs(L_motor)*SPEED[speed_mode]
            #pwm_l = int(((L_motor + 1) * 127.5)/SPEED[speed_mode])
            #pwm_r = int(((R_motor + 1) * 127.5)/SPEED[speed_mode])
            #print(f"L_motor: {L_motor}  R_motor: {R_motor}")
            pwm_l = int(((abs(L_motor) * 127.5) + 127.5)/SPEED[speed_mode])
            pwm_r = int(((abs(R_motor) * 127.5) + 127.5)/SPEED[speed_mode])
            #print(f"L_motor: {pwm_l}  R_motor: {pwm_r}")
            #pwm_r = abs(R_motor)*abs(R_motor)*SPEED[speed_mode]
    #         print(f"L_motor: {pwm_l}  R_motor: {pwm_r}")
    #         set_pwm(13, 0)  
    #         set_pwm(19, 0)
        else:
            pwm_l = 0
            pwm_r = 0
            mc_inn = [0, 0, 0, 0]

        print(mc_inn)
        pan_i = int(map_range(pan, 1, 179, 150, 600))
        tilt_i = int(map_range(tilt, 1, 179, 150, 600))
        integers = [pan_i, tilt_i, pwm_l, pwm_r]
        bool_byte = (mc_inn[0] << 0) | (mc_inn[1] << 1) | (mc_inn[2] << 2) | (mc_inn[3] << 3)
        #print(integers)
        data = struct.pack('>BIIIIB',0xFF, *integers, bool_byte)
        ser.write(data)
        #print(bin(bool_byte))
        #data = ser.read(17)
        #disp = data.hex()
        #if data:

        if (axis_values[0] + 0.01 < 1):
            axis_values[0] += 0.01
except KeyboardInterrupt:
    print("Exiting...")
finally:
    print("Exiting...")
