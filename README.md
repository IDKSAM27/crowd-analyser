**Head Detection with YOLOv5 and SORT Tracking**

This project is a Python-based application that uses YOLOv5 for head detection and SORT tracking for object tracking. It provides a graphical user interface (GUI) built with Tkinter 
to load videos or start webcam-based detection, displays results in real-time, and sounds an alarm when certain thresholds are met.

Features
  YOLOv5 Model Integration: Detects heads of people in videos or via webcam using a pre-trained YOLOv5 model.
  SORT Tracker: Tracks detected objects across frames for consistent identification.
  Tkinter GUI: Easy-to-use interface with options to load videos, start webcam detection, and stop detection.
  Alarm System: Plays an alert sound if the number of unique detections crosses a specified threshold.
  Optimizations:
    Detects in every 5th frame to reduce CPU load.
    Loads the YOLO model in a separate thread to improve application responsiveness.
    Alarm sound thread with a cooldown timer prevents overlapping alarms.

Requirements
Python Version
  Python 3.7 or above
Dependencies
  Install the required libraries using the following command:
  pip install -r requirements.txt

Required Libraries
  torch
  opencv-python
  Pillow
  playsound
  numpy
  tkinter (pre-installed with Python)
  sort (Include the sort.py file in the project directory)

Usage
Clone the Repository:
  git clone https://github.com/idksam27/Crowd_analyser.git

Place Alarm File:
  Download or save an alarm.mp3 file in the same directory as the script.

GUI Operations:

  Open Video: Load a video file and start detection.
  Start Webcam: Start real-time head detection using the webcam.
  Stop Detection: Stop video/webcam detection.
  
Detection Thresholds:

  Tracks heads of people in the video or live feed.
  Displays the total number of unique people and the number of people currently in the frame.
  Plays an alarm if the total count exceeds 55 unique detections (modifiable in the code).

File Structure

Crowd_analyer/
├── head_detection.py      # Main application file
├── alarm.mp3              # Alarm sound file (place in the same directory)
├── sort.py                # SORT tracking algorithm file
├── requirements.txt       # List of dependencies
└── README.md              # Documentation file

Notes
  The sort.py file is required for the tracking functionality. Ensure it's included in the same directory.
  The application processes every 5th frame of the video by default to reduce CPU load. You can modify the process_interval in the code as needed.
  If the alarm is not playing, verify the presence and path of alarm.mp3.

Future Improvements
  Add support for real-time saving of detected outputs (e.g., save frames with bounding boxes).
  Introduce a configuration file to make parameters like thresholds, frame intervals, and alarm settings customizable.
  Extend detection to include other objects or classes with minimal changes.

License
  This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
  Ultralytics YOLOv5 for the object detection model.
  SORT Tracker for multi-object tracking.
  Community contributions for libraries like OpenCV, Tkinter, and PyTorch.

  
