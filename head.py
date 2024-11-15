import cv2
import torch
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
from playsound import playsound
from sort import Sort
import numpy as np

# Initialize the main application window
root = tk.Tk()
root.title("Head Detection with YOLOv5 and SORT Tracking")
root.geometry("800x650")

# Make the window resizable only in height
root.resizable(width=False, height=True)

# Load the YOLOv5 model
def load_model():
    global model
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        print("YOLOv5 model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLOv5 model: {e}")

threading.Thread(target=load_model).start()

# Initialize SORT tracker
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Global variables for video capture and stopping the thread
cap = None
stop_thread = False
alarm_playing = False
tracked_ids = set()  # Keep track of unique IDs ever encountered
current_ids = set()  # Keep track of IDs currently in the frame

def open_video():
    global cap, stop_thread
    stop_thread = False
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=(("MP4 files", ".mp4"), ("All files", ".*")))
    
    if video_path:
        print(f"Selected video path: {video_path}")  # Debugging output
        cap = cv2.VideoCapture(video_path)
        
        # Check if the video was opened successfully
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video.")
            print("Error: Could not open video.")  # Debugging output
        else:
            print("Video opened successfully.")  # Debugging output
            threading.Thread(target=detect_people).start()  # Start detection in a new thread
    else:
        print("No video file selected.")  # Debugging output

def start_webcam():
    global cap, stop_thread
    stop_thread = False
    cap = cv2.VideoCapture(0)  # Open the default camera

    # Check if the webcam was opened successfully
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        print("Error: Could not open webcam.")  # Debugging output
    else:
        print("Webcam opened successfully.")  # Debugging output
        threading.Thread(target=detect_people).start()  # Start detection in a new thread

# Alarm will only sound once every 10 seconds
last_alarm_time = 0
alarm_interval = 10  

def play_alarm():
    global last_alarm_time
    current_time = time.time()
    if not alarm_playing and (current_time - last_alarm_time > alarm_interval):
        alarm_playing = True
        last_alarm_time = current_time
        playsound(r"alarm.mp3")
        alarm_playing = False

#starts to detect heads of people in every 5th frame of the vid
#TODO:  rectangular box issue
#remove try_except(if needed) to understand the rectangle box issue
def detect_people():

    try:
        global cap, stop_thread, tracked_ids, current_ids

        print("Starting people detection...")  # Debugging output

        frame_count = 0
        process_interval = 5  # Process every 5 frames

        while cap.isOpened() and not stop_thread:
            ret, frame = cap.read()
            if not ret:
                print("Warning: Could not read frame. Exiting detection loop.")
                break

            frame_count += 1
            if frame_count % process_interval != 0:
                continue
            
            frame = cv2.resize(frame, (640, 480))
            results = model(frame)

            # Extract bounding box results for 'person' class
            people = results.xyxy[0].cpu().numpy()
            people = [p for p in people if int(p[5]) == 0]  # Class 0 corresponds to 'person'

            # Prepare detections for SORT tracker (format: [x1, y1, x2, y2, score])
            detections = [[x1, y1, x2, y2, conf] for x1, y1, x2, y2, conf, _ in people]

            # Update the SORT tracker
            tracked_objects = tracker.update(np.array(detections))

            # Track and count unique person IDs
            current_ids = set()  # Reset for current frame
            for x1, y1, x2, y2, track_id in tracked_objects:
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                track_id = int(track_id)
                current_ids.add(track_id)

                # Calculate the head region (e.g., top 20% of the bounding box)
                head_height = int(0.25 * (y2 - y1))  # Adjust the fraction here for accuracy
                head_y2 = y1 + head_height

                # Draw bounding box for the head region only
                cv2.rectangle(frame, (x1, y1), (x2, head_y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Update the tracked_ids set to count unique detections
            tracked_ids.update(current_ids)

            # Update the count labels
            lbl_total_count.config(text=f"Total People Appeared: {len(tracked_ids)}")
            lbl_current_count.config(text=f"Current People in Frame: {len(current_ids)}")
            lbl_total_count.update_idletasks()
            lbl_current_count.update_idletasks()

            # Play the alarm if more than 10 unique people are detected
            if len(tracked_ids) > 10:
                threading.Thread(target=play_alarm).start()

            # Display the frame in the Tkinter window
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            lbl_video.imgtk = imgtk
            lbl_video.configure(image=imgtk)

            root.update()

            # Optional: Slow down processing to reduce CPU load
            time.sleep(0.03)

        # Release the video capture object
        cap.release()
        cv2.destroyAllWindows()
        print("Video capture released.")  # Debugging output

    except Exception as e:
        print(f"Error in detection loop: {e}")
        stop_detection() # Ensure resources are released 

def stop_detection():
    global stop_thread, tracked_ids, current_ids
    stop_thread = True
    lbl_video.configure(image='')  # Clear the video display
    lbl_total_count.config(text="Total People Appeared: 0")  # Reset total count display
    lbl_current_count.config(text="Current People in Frame: 0")  # Reset current count display
    tracked_ids.clear()  # Clear tracked IDs
    current_ids.clear()  # Clear current IDs
    print("Detection stopped.")  # Debugging output

# Creating GUI elements
lbl_video = tk.Label(root)
lbl_video.pack()

lbl_total_count = tk.Label(root, text="Total People Appeared: 0", font=("Arial", 14))
lbl_total_count.pack()

lbl_current_count = tk.Label(root, text="Current People in Frame: 0", font=("Arial", 14))
lbl_current_count.pack()

# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_open_video = tk.Button(button_frame, text="Open Video", command=open_video)
btn_open_video.pack(side=tk.LEFT, padx=10)

btn_webcam = tk.Button(button_frame, text="Start Webcam", command=start_webcam)
btn_webcam.pack(side=tk.LEFT, padx=10)

btn_stop = tk.Button(button_frame, text="Stop Detection", command=stop_detection)
btn_stop.pack(side=tk.LEFT, padx=10)

# Run the main Tkinter loop
root.mainloop()
#some slight improvements please check it, make any changes if necessary

#loading yolo in a seperate thread, should make the deploy faster
#detecting head in every 5th frame of the video, to reduce the load on cpu, we can change it accordingly, or remove it if any problems persist
#created seperate alarm thread with timer, to avoid overlapping alarm sounds