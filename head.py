import os
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
        lbl_status.config(text="Model loaded successfully.")
        print("YOLOv5 model loaded successfully.")
    except Exception as e:
        lbl_status.config(text="Failed to load model.")
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
    stop_thread = True  # Stop any previous detection thread
    time.sleep(0.1)  # Give time for previous threads to terminate
    if cap is not None:
        cap.release()  # Release previous video capture
    stop_thread = False  # Reset stop flag for new thread

    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        print("Error: Could not open webcam.")  # Debugging output
        return

    print("Webcam opened successfully.")  # Debugging output
    threading.Thread(target=detect_people, daemon=True).start()  # Start detection in a new thread

#Alarm will only sound once every 10 seconds
last_alarm_time = 0
alarm_interval = 10  

def play_alarm():
    global alarm_playing, last_alarm_time
    current_time = time.time()
    if not alarm_playing and (current_time - last_alarm_time > alarm_interval):
        alarm_playing = True
        last_alarm_time = current_time
        try:
            # Construct the path dynamically
            script_dir = os.path.dirname(os.path.abspath(__file__))
            alarm_path = os.path.join(script_dir, "alarm.mp3")
            playsound(alarm_path)
        except Exception as e:
            print(f"Error playing alarm: {e}")
        finally:
            alarm_playing = False


#starts to detect heads of people in every 5th frame of the vid
#remove try_except(if needed) to understand the rectangle box issue
def detect_people():
    try:
        global cap, stop_thread, tracked_ids, current_ids
        print("Starting people detection...")

        frame_count = 0
        process_interval = 5  # Process every 5 frames

        while cap.isOpened() and not stop_thread:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Warning: Invalid frame received. Skipping.")
                time.sleep(0.1)
                continue

            frame_count += 1
            if frame_count % process_interval != 0:
                continue

            try:
                frame = cv2.resize(frame, (640, 480))
                results = model(frame)

                if len(results.xyxy) == 0 or results.xyxy[0].shape[1] < 6:
                    print("Warning: Model output is invalid. Skipping frame.")
                    continue

                # Extract bounding box results for 'person' class
                people = results.xyxy[0].cpu().numpy()
                people = [p for p in people if int(p[5]) == 0]  # Class 0 corresponds to 'person'

                # Prepare detections for SORT tracker
                detections = [[x1, y1, x2, y2, conf] for x1, y1, x2, y2, conf, _ in people]

                # Update the SORT tracker
                tracked_objects = tracker.update(np.array(detections))

                current_ids = set()
                for x1, y1, x2, y2, track_id in tracked_objects:
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    track_id = int(track_id)
                    current_ids.add(track_id)

                    # Calculate the head region (top 25% of the bounding box)
                    head_height = int(0.25 * (y2 - y1))  # Adjust for more/less head region
                    head_y2 = y1 + head_height

                    # Draw a bounding box for the head region
                    cv2.rectangle(frame, (x1, y1), (x2, head_y2), (0, 255, 0), 2)  # Green rectangle
                    cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                # Update tracked IDs
                tracked_ids.update(current_ids)

                # Update GUI labels
                lbl_total_count.config(text=f"Total People Appeared: {len(tracked_ids)}")
                lbl_current_count.config(text=f"Current People in Frame: {len(current_ids)}")

                # Display the frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                lbl_video.imgtk = imgtk
                lbl_video.configure(image=imgtk)

                root.update()
                time.sleep(0.03)
            except Exception as inner_e:
                print(f"Error processing frame: {inner_e}")

        cap.release()
        cv2.destroyAllWindows()
        print("Video capture released.")

    except Exception as e:
        print(f"Error in detection loop: {e}")

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

lbl_status = tk.Label(root, text="Loading model...", font=("Arial", 14))
lbl_status.pack()

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