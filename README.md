# CS-4513 (Senior Software Projects) at The University of Tulsa

## Project Name
A Software Application for Making a Robot Autonomous in an OptiTrack Environment

## Timeframe
Feburary-May 2025

## Team Members
Anastasia Reed, Back-End Developer

<img src="https://github.com/user-attachments/assets/13c7c4b5-01e1-4857-8cd6-e8916faf0d29" alt="Anastasia Reed" width="250"/>

Bio: I am a Computer Science major, minoring in Mathematics. When I'm not working or studying, I'm usually reading, playing video games, or painting.

Caleb Tietz, Back-End Lead

<img src="https://github.com/user-attachments/assets/067086dd-c7e4-44c0-bdff-881d97af4194" alt="Caleb Tietz" width="250"/>

Bio: I am a Computer Science major with a minor in mathematics. I currently work at my church and as a math tutor. When I'm not at school or work, I'm usually spending time with my fiancé, playing board games or video games, or writing hobby code projects.

Rhea Katari, Front-End Developer

<img src="https://github.com/user-attachments/assets/1b4a95e0-f22e-4147-88d8-0eed68dd2c4f" alt="Rhea Katari" width="250"/>

Bio: I am double majoring in Computer Science and Cyber Security and minoring in Mathematics. When I'm not in class, you'll usually find me listening to music, reading, or diving into geography and history.

Riley Raasch, Project and Front-End Lead

<img src="https://github.com/user-attachments/assets/71f2dfa0-b72f-4fef-9ae0-81755e5c7b40" alt="Riley Raasch" width="250"/>

Bio: I am a Computer Science major, minoring in Cyber Security and Mathematics. Currently, I am working at the Bank of Oklahoma as an information security intern. Outside of school and work, you'll most likely find me watching Doctor Who, playing video games, or spoiling my cat.

## Faculty Supervisor
Will Friedel

<img src="https://github.com/user-attachments/assets/0f790bfe-61b7-4ae2-8cb8-296997ea35bb" alt="Will Friedel" width="250"/>

Bio: William Friedel worked as an electrical engineer at a government contractor for four years before joining TU as ECE lab manager and instructor of digital and embedded systems in 2022.

## About the Project
Professor William Friedel has built a robot but needs the software to be developed to make the robot autonomous in an OptiTrack environment. The robot is built on a Roomba frame and includes an Arduino and Raspberry Pi to control its movements, as well as a camera on top for visuals. 

OptiTrack is a motion capture system that includes specialized cameras, markers, tracking, and software. The cameras can see infrared light and the markers can reflect it. This allows the cameras to track the markers’ movement and the software to construct a 3D model of the movement from that provided data. The robot and the OptiTrack environment setup are both located on campus.

The project will require us to build a graphical user interface (GUI) to remotely control the robot and Python scripts to collect the OptiTrack location data, camera data, and automate tasks/control the robot. The GUI will provide an intuitive way to visualize the robot’s position in real time and allow for manual control if necessary. Additionally, it will display critical system information such as battery levels, movement commands, and sensor feedback.

The software development process will involve integrating multiple hardware and software components. The Arduino will be responsible for low-level motor control, receiving movement commands from a Raspberry Pi, which will act as the main processing unit. The Raspberry Pi will handle higher-level computations, such as processing camera feeds and communicating with the OptiTrack system. Python scripts will be written to retrieve positional data from OptiTrack, interpret the robot’s location, and send movement commands accordingly to navigate autonomously.

Another crucial aspect of the project is testing and debugging the system to ensure seamless integration. We will conduct multiple test runs in the OptiTrack environment to verify the accuracy of movement commands, response times, and tracking precision. Adjustments will be made based on real-time feedback to refine the control algorithms and improve autonomy.

Ultimately, this project will result in a functional, semi-autonomous robot capable of navigating within the OptiTrack system, with a well-structured software stack that allows for both automated and manual operation. This work will contribute to future research in robotics, motion tracking, and control systems.
