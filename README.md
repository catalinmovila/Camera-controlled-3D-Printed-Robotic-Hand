# Camera-controlled 3D-Printed Robotic Hand

This repository contains the code and documentation for a **camera-controlled 3D-printed robotic hand**.  
The system combines:

- a **3D-printed hand** actuated by five servo motors  
- an **ESP32** microcontroller running Arduino code  
- **Python** scripts using a webcam to track hand movements and send control commands.

The project was developed as a special course in Biomedical Engineering and explores how gesture tracking and embedded control can be used for **assistive / rehabilitation-oriented applications**.

<img width="400" height="600" alt="image" src="https://github.com/user-attachments/assets/c80ed5cc-5c09-4b82-95fe-250a61b493c7" />


https://github.com/user-attachments/assets/dcea9955-e7e7-4b32-bb40-bbebe6e803f0


---

## Features

- **3D-printed robotic hand**
  - Five servo-driven fingers based on a Parallax-style design
  - Individual finger actuation via flexible wires and continuous rotation servos :contentReference[oaicite:1]{index=1}  

- **ESP32-based control**
  - Arduino sketch for reading serial commands and driving each servo
  - PWM control of finger motion (open / close / custom gestures)

- **Camera & hand-tracking (Python)**
  - Webcam input processed with OpenCV
  - Hand-tracking and gesture extraction (MediaPipe-style pipeline)
  - Mapping of detected gestures or keyboard commands to servo control signals

- **Demo material**
  - Short demo videos showing different gestures and hand motion
  - PDF report with detailed explanation of hardware, electronics and design decisions :contentReference[oaicite:2]{index=2}
