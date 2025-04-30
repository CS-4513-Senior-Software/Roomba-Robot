#!/home/will/main/venv/bin/python
import time
import math
import socket
import struct
import serial
from serial import Serial
import pygame
import typing
from picamera2 import Picamera2
import cv2
import io
import csv
import threading

class DigitalWriteException(Exception):
    pass

cam = Picamera2()
cam.preview_configuration.main.size = (640, 480)
cam.preview_configuration.main.format = "RGB888"
cam.configure("video")

cam.start()
time.sleep(2) # allow camera to conduct auto exposure adjustments

prev_integers = [450, 450, 0, 0]
prev_bool_byte = 0
SPEED = [1, 2, 3, 4, 5, 6]
speed_mode = 0
mc_inn = [0,0,0,0]

INHIBIT_MOTION = 1

AXIS_TILT = 3
AXIS_PAN = 2
AXIS_FB = 1
AXIS_LR = 0

otData = {
    "x": 0,
    "y": 0,
    "z": 0,
    "roll": 0,
    "pitch": 0,
    "yaw": 0
}

def setOtData(x: float, y: float, z: float, rot):
    """
    Will set the x, y, and z position data as floats.
    Will convert the Quaterion rotation _rot_ to euler
    angles: roll, pitch, and yaw, in degrees.
    """
    print("setOtData")
    otData["x"] = x
    otData["y"] = -y
    otData["z"] = z
    otData["roll"], otData["pitch"], otData["yaw"] = quaternion_to_euler(rot)
    
    csv_file = open('otData.csv', mode='w', newline='')
    csv_writer = csv.writer(csv_file)
    row = []
    for item in otData:
        row.append(otData[item])
    csv_writer.writerow(row)

def quaternion_to_euler(quaternion):    
    """
    Convert a quaternion into Euler angles (roll, pitch, yaw) in degrees.
    Roll is rotation around x-axis
    Pitch is rotation around y-axis
    Yaw is rotation around z-axis
    """
    qx, qy, qz, qw = quaternion
    
    # Normalize the quaternion
    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    qx /= norm
    qy /= norm
    qz /= norm
    qw /= norm

    # Roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll_rad = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        # Use 90 degrees if out of range
        pitch_rad = math.copysign(math.pi / 2, sinp)
    else:
        pitch_rad = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw_rad = math.atan2(siny_cosp, cosy_cosp)

    # Convert radians to degrees
    roll = math.degrees(roll_rad)
    pitch = math.degrees(pitch_rad)
    yaw = math.degrees(yaw_rad)

    return roll, pitch, yaw

def calculate_angle(x_start, y_start, x_end, y_end):
    """Calculate the angle to the endpoint."""
    
    print("x_start: " + str(x_start))
    print("x_end: " + str(x_end))
    print("y_start: " + str(y_start))
    print("y_end: " + str(y_end))
    
    angle_rad = math.atan2(y_end - y_start, x_end - x_start)
    # angle_deg = math.degrees(angle_rad) + 180
    angle_deg = math.degrees(angle_rad)
    angle_deg = (angle_deg + 180) % 360 - 180  # Normalize to [-180, 180]
    print("angle_deg " + str(angle_deg))
    return angle_deg

def calculate_rotation(current_angle, target_angle):
    # """Calculate the shortest rotation direction needed to face the target angle."""
    # angles_to_rotate = target_angle - current_angle
    # return angles_to_rotate
    """Return the shortest signed angle difference in degrees."""
    return ((target_angle - current_angle + 180) % 360) - 180

def move_to_endpoint(x_end, y_end, tolerance=0.1):
    """
    Navigate the robot to the specified endpoint.
    :param x_end: Target x-coordinate.
    :param z_end: Target z-coordinate.
    :param tolerance: Distance tolerance to consider the endpoint reached.
    """
    global otData


    movingForward = False
    while True:
        print("hit")
        
        # Get the current position and orientation from OptiTrack data
        with open('otData.csv', mode='r') as file:
            reader = csv.reader(file)

            for row in reader:
                otData["x"] = float(row[0])
                otData["y"] = float(row[1])
                otData["z"] = float(row[2])
                otData["roll"] = float(row[3])
                otData["pitch"] = float(row[4])
                # otData["yaw"] = (float(row[5]) + float(180))
                otData["yaw"] = ((float(row[5]) + 180) % 360) - 180

        x_start, y_start = otData["x"], otData["y"]
        current_angle = otData["yaw"]
        
        # csv_writer.writerow([current_angle, otData["qx"], otData["qy"], otData["qz"], otData["qw"], time.time()])
        

        # Calculate the distance to the endpoint
        distance = math.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
        if distance < tolerance:
            print("Reached the endpoint.")
            # Stop the robot
            digital_write([0, 0, 0, 0])
            break

        # Calculate the target angle
        target_angle = calculate_angle(x_start, y_start, x_end, y_end)
        print("target " + str(target_angle))
        print("current " + str(current_angle))

        # Rotate to face the target angle
        angles_to_rotate = target_angle - current_angle
        
        old_dir = 0
        if abs(angles_to_rotate) > 45:
            last_angle_diff = None
            while abs(angles_to_rotate) > 10: # rotate while not aligned
                # Get the current position and orientation from OptiTrack data
                with open('otData.csv', mode='r') as file:
                    reader = csv.reader(file)

                    for row in reader:
                        if len(row) >= 6:
                            otData["x"] = float(row[0])
                            otData["y"] = float(row[1])
                            otData["z"] = float(row[2])
                            otData["roll"] = float(row[3])
                            otData["pitch"] = float(row[4])
                            # otData["yaw"] = (float(row[5]) + float(180))
                            otData["yaw"] = ((float(row[5]) + 180) % 360) - 180
                # current_angle = otData["yaw"]
                # target_angle = calculate_angle(x_start, y_start, x_end, y_end)
                x_start, y_start = otData["x"], otData["y"]
                current_angle = otData["yaw"]
                target_angle = calculate_angle(x_start, y_start, x_end, y_end)
                movingForward = False
                print("test")
                current_angle = otData["yaw"]
                # angles_to_rotate = target_angle - current_angle
                angles_to_rotate = calculate_rotation(current_angle, target_angle)
                print("angles to rotate: " + str(angles_to_rotate))
                print("target " + str(target_angle))
                print("current " + str(current_angle))
                print("x " + str(otData["x"]))
                print("y " + str(otData["y"]))
                print("z " + str(otData["z"]))

                # added check for oscillation
                if last_angle_diff is not None and abs(angles_to_rotate - last_angle_diff) < 0.5:
                    print("Detected angle oscillation, exiting rotation loop.")
                    break
                last_angle_diff = angles_to_rotate
                
                # Determine shortest direction to rotate
                # if angles_to_rotate > 0:
                #    rotation_dir = -0.1
                # else:
                #    rotation_dir = 0.1
                
                # proportional control for rotation speed
                rotation_dir = clamp(-0.01 * angles_to_rotate, -0.5, 0.5)

                axis_values = [rotation_dir, 0, 0, 0] # rotate in place
                digital_write(axis_values)
                # if old_dir != rotation_dir:
                #     # print("change direction")
                #     old_dir = rotation_dir
        
        # if not movingForward:
            # movingForward = True
        axis_values = [0, 0.5, 0, 0] # move forward once aligned
            # Send movement commands using existing motor control logic
        digital_write(axis_values)


def generate_frames():
    """Generator function to capture frames from Pi Camera and yield them as JPEGs."""
    while True:
        frame = cam.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def digital_write(axis_values: list[int], easing = False, n_steps = 15):
    global prev_integers
    global prev_bool_byte
    global ser
    
    try:
        if len(axis_values) != 4:
            raise DigitalWriteException("Length of axis_values array must be equal to 4.")

        if (ser.in_waiting > 0):
            line = ser.readline().decode('utf-8').strip()
            print("test")
            print(line)

        data = get_integers_bool(axis_values)
        endInts = data["ints"]
        bool_byte = data["bool_byte"]
    
        if (not easing):
            data = struct.pack('>BIIIIB',0xFF, *endInts, bool_byte)
            # print("writing")
            ser.write(data)
            return
    except serial.SerialException as e:
        print(f"Serial Exception: {e}")

    except Exception as e:
        print(f"General Error: {e}")
    
    # should we remove math.ceil function from stepSize calculation?
    stepSize0 = math.ceil((endInts[0] - prev_integers[0]) / n_steps)
    stepSize1 = math.ceil((endInts[1] - prev_integers[1]) / n_steps)
    stepSize2 = math.ceil((endInts[2] - prev_integers[2]) / n_steps)
    stepSize3 = math.ceil((endInts[3] - prev_integers[3]) / n_steps)
    
    stepSizes = [stepSize0, stepSize1, stepSize2, stepSize3]
    
    for i in range(n_steps):
        for j, k in enumerate(prev_integers):
            stepSize = stepSizes[j]
            prev_integers[j] += stepSize
            data = struct.pack('>BIIIIB',0xFF, *prev_integers, bool_byte)
            ser.write(data)
    
    # Possible changes
    # for i in range(n_steps):
    #    for j in range(4):
    #        prev_integers[j] += stepSizes[j]
    #    # Convert floating-point values to integers when sending the data
    #    data = struct.pack('>BIIIIB', 0xFF, *map(int, prev_integers), bool_byte)
    #    ser.write(data)
    #    time.sleep(0.01)  # Add a small delay to ensure smooth transition
    
    # copy endInts into prev_integers
    prev_integers = []
    for i in endInts:
        prev_integers.append(i)
    prev_bool_byte = bool_byte

# Process the joystick axis values and map them to motor and servo commands
# Handle button inputs to adjust speed and reset servos
def get_integers_bool(axis_values: list[int]):
    global pan
    global tilt
    global speed_mode
    
    button_values = 0
        
    # servos
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
    
    L_motor = axis_values[AXIS_FB] - axis_values[AXIS_LR]
    R_motor = axis_values[AXIS_FB] + axis_values[AXIS_LR]
    L_motor = clamp(L_motor, -1, 1)
    R_motor = clamp(R_motor, -1, 1)
    # print("L_motor " + str(L_motor))
    # print("R_motor " + str(R_motor))

    if(abs(L_motor) > 0.01 or abs(R_motor) > 0.01):
        if(L_motor <= 0 and R_motor <= 0): # Reverse
            mc_inn = [1, 0, 1, 0]
        elif(L_motor <= 0 and R_motor > 0):
            mc_inn = [0, 1, 1, 0]
        elif(L_motor > 0 and R_motor <= 0):
            mc_inn = [1, 0, 0, 1]
        elif(L_motor > 0 and R_motor > 0): #Forward
            mc_inn = [0, 1, 0, 1]
        pwm_l = int(((abs(L_motor) * 127.5) + 127.5))
        pwm_r = int(((abs(R_motor) * 127.5) + 127.5))
    else:
        pwm_l = 0
        pwm_r = 0
        mc_inn = [0, 0, 0, 0]

    pan_i = int(map_range(pan, 1, 179, 150, 600))
    tilt_i = int(map_range(tilt, 1, 179, 150, 600))
    integers = [pan_i, tilt_i, pwm_l, pwm_r]
    # print(integers)
    bool_byte = (mc_inn[0] << 0) | (mc_inn[1] << 1) | (mc_inn[2] << 2) | (mc_inn[3] << 3)
    
    return {
        "ints": integers,
        "bool_byte": bool_byte
    }
  
try:  
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("Serial port connected successfully")

except serial.SerialException:
    print("ERROR: Unable to connect to serial port. Check USB connection.")
    exit()

# Ensure values stay within a specified range
def clamp(value, min_value, max_value):
    """Clamp the value between min_value and max_value."""
    if(abs(value) < 0.001):
        value = 0
    return max(min(value, max_value), min_value)

# Map a value from one range to another
def map_range(value, min_old, max_old, min_new, max_new):
    return min_new + (value - min_old) * (max_new - min_new) / (max_old - min_old)


time.sleep(2)  # Give Arduino time to reset

# Servo
pan = 120; # default straight is 120
tilt = 100; # default level is 100
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

try:
        
    # pygame.event.pump()
    
    # axis_values = []
    # for i in range(4):
    #     axis_value = joystick.get_axis(i)
    #     axis_values.append(axis_value)
    
    pass
        
    
    # axis_values = [0, -1, 0, 0]
    # print(prev_integers)
    # digital_write(axis_values)
    # print(prev_integers)
    # time.sleep(2)
    # axis_values = [0, 0.1, 0, 0]
    # digital_write(axis_values)
    
except KeyboardInterrupt:
    print("Exiting...")
finally:
    print("Exiting...")
