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
    otData["x"] = x
    otData["y"] = y
    otData["z"] = z
    otData["roll"], otData["pitch"], otData["yaw"] = quaternion_to_euler(rot)

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

def calculate_angle(x_start, z_start, x_end, z_end):
    """Calculate the angle to the endpoint."""
    return math.atan2(z_end - z_start, x_end - x_start)

def rotate_to_angle(current_angle, target_angle):
    """Calculate the shortest rotation needed to face the target angle."""
    rotation = target_angle - current_angle
    if rotation > math.pi:
        rotation -= 2 * math.pi
    elif rotation < -math.pi:
        rotation += 2 * math.pi
    return rotation

def move_to_endpoint(x_end, z_end, tolerance=0.1):
    """
    Navigate the robot to the specified endpoint.
    :param x_end: Target x-coordinate.
    :param z_end: Target z-coordinate.
    :param tolerance: Distance tolerance to consider the endpoint reached.
    """
    global otData

    while True:
        # Get the current position and orientation from OptiTrack data
        x_start, z_start = otData["x"], otData["z"]
        current_angle = otData["rot"]

        # Calculate the distance to the endpoint
        distance = math.sqrt((x_end - x_start) ** 2 + (z_end - z_start) ** 2)
        if distance < tolerance:
            print("Reached the endpoint.")
            # Stop the robot
            digital_write([0, 0, 0, 0])
            break

        # Calculate the target angle
        target_angle = calculate_angle(x_start, z_start, x_end, z_end)

        # Rotate to face the target angle
        rotation = rotate_to_angle(current_angle, target_angle)
        if abs(rotation) > 0.1:  # Rotate if not aligned
            axis_values = [rotation, 0, 0, 0]  # Rotate in place
        else:  # Move forward if aligned
            axis_values = [0, 0.5, 0, 0]  # Move forward

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

def digital_write(axis_values: list[int], easing = True, n_steps = 15):
    global prev_integers
    global prev_bool_byte
    global ser
    
    print(otData)
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
