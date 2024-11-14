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
root.title("Head Detection from Full Body")
root.geometry("800x650")

# Load YOLOv5 model (using pre-trained YOLOv5s model)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Initialize SORT tracker
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Global variables for video capture and stopping the thread
cap = None
stop_thread = False
alarm_playing = False
tracked_ids = set()  # Keep track of unique IDs

# opens file explorer from which the video shall be selected
def open_video():
    global cap, stop_thread
    stop_thread = False
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=(("MP4 files", ".mp4"), ("All files", ".*")))
    
    if video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video.")
        else:
            threading.Thread(target=detect_heads).start()

# opens the webcam or any camera which is linked or connected with the pc
def start_webcam():
    global cap, stop_thread
    stop_thread = False
    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
    else:
        threading.Thread(target=detect_heads).start()

def play_alarm():
    global alarm_playing
    if not alarm_playing:
        alarm_playing = True
        playsound(r"alarm.mp3")
        alarm_playing = False

def detect_heads():
    global cap, stop_thread, tracked_ids

    while cap.isOpened() and not stop_thread:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))
        
        # Perform detection with YOLOv5
        results = model(frame)
        
        # Filter detections for 'person' class (YOLOv5 default model detects people)
        detections = []
        for *box, conf, cls in results.xyxy[0].cpu().numpy():
            if int(cls) == 0:  # Class 0 corresponds to 'person' in the YOLOv5 model
                x1, y1, x2, y2 = map(int, box)
                detections.append([x1, y1, x2, y2, conf])
        
        # Update SORT tracker
        tracked_objects = tracker.update(np.array(detections))

        current_ids = set()
        for x1, y1, x2, y2, track_id in tracked_objects:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            track_id = int(track_id)
            current_ids.add(track_id)

            # Calculate the head region (upper third of the bounding box)
            head_height = (y2 - y1) // 3
            head_y2 = y1 + head_height

            # Draw bounding box for the head region
            cv2.rectangle(frame, (x1, y1), (x2, head_y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Person ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        tracked_ids.update(current_ids)
        lbl_count.config(text=f"Unique Head Count: {len(tracked_ids)}")
        lbl_count.update_idletasks()

        # Play the alarm if more than 10 unique heads are detected
        if len(tracked_ids) > 10:
            threading.Thread(target=play_alarm).start()

        # Display the frame in the Tkinter window
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        
        root.update()
        time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()

def stop_detection():
    global stop_thread, tracked_ids
    stop_thread = True
    lbl_video.configure(image='')
    lbl_count.config(text="Unique Head Count: 0")
    tracked_ids.clear()

# Creating GUI elements
lbl_video = tk.Label(root)
lbl_video.pack()

lbl_count = tk.Label(root, text="Unique Head Count: 0", font=("Arial", 14))
lbl_count.pack()

btn_open_video = tk.Button(root, text="Open Video", command=open_video)
btn_open_video.pack(side=tk.LEFT, padx=10, pady=10)

btn_webcam = tk.Button(root, text="Start Webcam", command=start_webcam)
btn_webcam.pack(side=tk.LEFT, padx=10, pady=10)

btn_stop = tk.Button(root, text="Stop Detection", command=stop_detection)
btn_stop.pack(side=tk.LEFT, padx=10, pady=10)

# Run the main Tkinter loop
root.mainloop()