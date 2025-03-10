
# Crowd Detection with YOLOv5 and SORT Tracking

This project is a Python-based application that uses YOLOv5 for head detection and SORT tracking for object tracking. It provides a graphical user interface (GUI) built with Tkinter 
to load videos or start webcam-based detection, displays results in real-time, and sounds an alarm when certain thresholds are met.

Also has a [mobile application](https://github.com/IDKSAM27/Crowd_detector) (WIP)

## Features

* **YOLOv5 Model Integration:** Detects heads of people in videos or via webcam using a pre-trained YOLOv5 model.

* **SORT Tracker:** Tracks detected objects across frames for consistent identification.

* **Tkinter GUI:** Easy-to-use interface with options to load videos, start webcam detection, and stop detection.

* **Alarm System:** Plays an alert sound if the number of unique detections crosses a specified threshold.

* **Optimizations:**
    
    * Detects in every 5th frame to reduce CPU load.

    * Loads the YOLO model in a separate thread to improve application responsiveness.

    * Alarm sound thread with a cooldown timer prevents overlapping alarms.
      
* **Visual Representation:**

    * Usage of Bar and Line graph to visually represent the head count of the crowd per minute (can also implement per hour if needed).
 
    * The program counts the total number of people appeared in a minute and save the count in a dictionary, then the count is reset, and the next minute data is captured.
 
    * ROI (Region of Interest), where you could select a particular region in the video footage and the algo will focus on only the specified region.
    

## Documentation(detailed)

[Documentation](https://github.com/IDKSAM27/Crowd-analyser/blob/main/Documentation.txt): read this file for more detailed instructions on installation and use.
(P.S., I would prefer you to read this first as it has more deep info!)

## Requirements
### Python Version
* Python 3.7 or above
### Dependencies
Install the required libraries using the following command:
```bash
  pip install -r requirements.txt
```
#### Required Libraries
* `torch`
* `opencv-python`
* `Pillow`
* `playsound`
* `numpy`
* `tkinter`
* `sort` (Include the `sort.py` file in the project directory)
* `matplotlib`
* `ttkbootstrap`


## Usage

### 1. Clone the repository:

```bash
  git clone https://github.com/IDKSAM27/crowd-analyser
```

### 2. Place Alarm File:
* Download or save an `alarm.mp3` file in the same directory as the script.

### 3. Run the Application:

```bash
  python head.py
```

### 4. GUI Operations:
* **Open Video:** Load a video file and start detection.
* **Start Webcam:** Start real-time head detection using the Webcam
* **Stop Detection:** Stop video/webcam detection.
* **Display Minute Counts:** Displays line and bar graph of the occured data.
* **Select and Clear ROI:** Enable user to select and clear Region of Interest.

### 5. Detection Thresholds:
* **Track heads** of people in the video or live feed.
* **Displays** the total nubmer of unique people and the number of people currently in the frame.
* **Plays an alarm** in the total count exceeds 60 unique detection (modifiable in the code).




## File Structure

```graphql
Crowd_analysis/
├── head.py      # Main application file
├── graph_display.py       # Display graphs
├── alarm.mp3              # Alarm sound file (place in the same directory)
├── sort.py                # SORT tracking algorithm file
├── requirements.txt       # List of dependencies
├── Documentation.txt      # Detailed Documentation
└── README.md              # basic doc file

```


## Notes

* The `sort.py` file is required for the tracking functionality. Ensure it's included in the same directory.
* The application processes every 5th frame of the video by default to reduce CPU load. You can modify the `process_interval` in the code as needed.
* If the alarm is not playing, verify the presence and path of `alarm.mp3`.
* Always make sure to create 'virtual environment' before installing the requirements or libraries.


## Future Improvements

* Add support for real-time saving of detected outputs (e.g., save frames with bounding boxes).
* Introduce a configuration file to make parameters like thresholds, frame intervals, and alarm settings customizable.
* Extend detection to include other objects or classes with minimal changes.


## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.




## Acknowledgments

* [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5) for the object detection model.
* [SORT Tracker](https://github.com/abewley/sort) for multi-object tracking.
* Community contributions for libraries like OpenCV, Tkinter, and PyTorch.