# CS-4513 (Senior Software Projects) at The University of Tulsa

## Project Name
A Software Application for Making a Robot Autonomous in an OptiTrack Environment

## Timeframe
Feburary-May 2025

## Team Members
Anastasia Reed, Back-End Developer

Picture:

Bio: I am a Computer Science major, minoring in Mathematics. When I'm not working or studying, I'm usually reading, playing video games, or painting.

Caleb Tietz, Back-End Lead

Picture:

Bio:

Rhea Katari, Front-End Developer

Picture:

Bio:

Riley Raasch, Project and Front-End Lead

Picture:

![image](https://github.com/user-attachments/assets/71f2dfa0-b72f-4fef-9ae0-81755e5c7b40)

Bio: I am a Computer Science major, minoring in Cyber Security and Mathematics. Currently, I am working at the Bank of Oklahoma as an information security intern. Outside of school and work, you'll most likely find me watching Doctor Who, playing video games, or spoiling my cat.

## Faculty Supervisor
Will Friedel

## Group Picture (add if we want)

## About the Project
Professor William Friedel has built a robot but needs the software to be developed to make the robot autonomous in an OptiTrack environment. The robot is built on a Roomba frame and includes an Arduino and Raspberry Pi to control its movements, as well as a camera on top for visuals. 

OptiTrack is a motion capture system that includes specialized cameras, markers, tracking, and software. The cameras can see infrared light and the markers can reflect it. This allows the cameras to track the markers’ movement and the software to construct a 3D model of the movement from that provided data. The robot and the OptiTrack environment setup are both located on campus.

The project will require us to build a graphical user interface (GUI) to remotely control the robot and Python scripts to collect the OptiTrack location data, camera data, and automate tasks/control the robot. The GUI will provide an intuitive way to visualize the robot’s position in real time and allow for manual control if necessary. Additionally, it will display critical system information such as battery levels, movement commands, and sensor feedback.

The software development process will involve integrating multiple hardware and software components. The Arduino will be responsible for low-level motor control, receiving movement commands from a Raspberry Pi, which will act as the main processing unit. The Raspberry Pi will handle higher-level computations, such as processing camera feeds and communicating with the OptiTrack system. Python scripts will be written to retrieve positional data from OptiTrack, interpret the robot’s location, and send movement commands accordingly to navigate autonomously.

Another crucial aspect of the project is testing and debugging the system to ensure seamless integration. We will conduct multiple test runs in the OptiTrack environment to verify the accuracy of movement commands, response times, and tracking precision. Adjustments will be made based on real-time feedback to refine the control algorithms and improve autonomy.

Ultimately, this project will result in a functional, semi-autonomous robot capable of navigating within the OptiTrack system, with a well-structured software stack that allows for both automated and manual operation. This work will contribute to future research in robotics, motion tracking, and control systems.
