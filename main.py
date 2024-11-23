#==================================================================================================

#the base code of this project, it has nothing to do with the working project!!

#you can delete this file if you want.

#going through this code is the best way to understand the base of this project.

#==================================================================================================

import cv2
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
from playsound import playsound

# Initialize the main application window
root = tk.Tk()
root.title("Crowd Detection with Count and Alarm")
root.geometry("800x650")

# Load the Haar cascade for full body detection
body_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

# Global variables for video capture, stopping the thread, and counting people
cap = None
stop_thread = False
alarm_playing = False  # Flag to prevent repeated alarm sounds

def open_video():
    global cap, stop_thread
    stop_thread = False  # Reset stop flag
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=(("MP4 files", ".mp4"), ("All files", ".*")))
    if video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video.")
        else:
            threading.Thread(target=detect_crowd).start()  # Start detection in a new thread

def start_webcam():
    global cap, stop_thread
    stop_thread = False  # Reset stop flag
    cap = cv2.VideoCapture(0)  # Opens default camera
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
    else:
        threading.Thread(target=detect_crowd).start()  # Start detection in a new thread

def play_alarm():
    global alarm_playing
    if not alarm_playing:  # Prevent multiple alarms playing simultaneously
        alarm_playing = True
        playsound(r"alarm.mp3")
        alarm_playing = False

def detect_crowd():
    global cap, stop_thread
    while cap.isOpened() and not stop_thread:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame for faster processing
        frame = cv2.resize(frame, (640, 480))
        
        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect people in the frame
        bodies = body_classifier.detectMultiScale(gray, 1.1, 4)  # Adjusted parameters for better detection
        
        # Count the number of people detected
        people_count = len(bodies)

        # If more than 10 people detected, play alarm sound
        if people_count > 10:
            threading.Thread(target=play_alarm).start()  # Start alarm sound in a new thread
        
        # Draw rectangles around each detected person and show the count
        for (x, y, w, h) in bodies:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Person', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Update the count label and refresh it
        lbl_count.config(text=f"People Count: {people_count}")
        lbl_count.update_idletasks()  # Explicitly refresh the count display
        
        # Display the frame in the Tkinter window
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        
        root.update()

        # Optional: Slow down processing to reduce CPU load
        time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()

def stop_detection():
    global stop_thread
    stop_thread = True  # Set the flag to stop the thread
    lbl_video.configure(image='')  # Clear the video display
    lbl_count.config(text="People Count: 0")  # Reset count display

# Creating GUI elements
lbl_video = tk.Label(root)
lbl_video.pack()

lbl_count = tk.Label(root, text="People Count: 0", font=("Arial", 14))
lbl_count.pack()

btn_open_video = tk.Button(root, text="Open Video", command=open_video)
btn_open_video.pack(side=tk.LEFT, padx=10, pady=10)

btn_webcam = tk.Button(root, text="Start Webcam", command=start_webcam)
btn_webcam.pack(side=tk.LEFT, padx=10, pady=10)

btn_stop = tk.Button(root, text="Stop Detection", command=stop_detection)
btn_stop.pack(side=tk.LEFT, padx=10, pady=10)

# Run the main Tkinter loop
root.mainloop()