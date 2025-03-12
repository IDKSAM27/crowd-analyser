# For comparison, below system uses tkinter whereas above uses PyQt
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import face_recognition


# Initialize the main application window
root = tk.Tk()
root.title("Face Detection and Recognition")
root.geometry("800x660")
root.resizable(width=True, height=True)

# Global variables
cap = None
stop_thread = False
face_encodings = []
face_names = []

# Load pre-trained face dataset
def load_face_dataset():
    global face_encodings, face_names
    dataset_path = filedialog.askdirectory(title="Select Face Dataset Folder")

    if not dataset_path:
        messagebox.showinfo("Info", "No folder selected.")
        return

    face_encodings.clear()
    face_names.clear()

    try:
        for file_name in os.listdir(dataset_path):
            if file_name.endswith(('.jpg', '.png')):
                image_path = os.path.join(dataset_path, file_name)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)

                if encoding:
                    face_encodings.append(encoding[0])
                    face_names.append(os.path.splitext(file_name)[0])

        messagebox.showinfo("Info", f"Loaded {len(face_names)} faces from the dataset.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load dataset: {e}")

# Open a video file

def open_video():
    global cap, stop_thread
    stop_thread = False
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=(("MP4 files", ".mp4"), ("All files", ".*")))

    if video_path:
        print(f"Selected video path: {video_path}") # Debugging output
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video.")
            print("Error: Could not open video.") # Debugging output  
        else:
            print("Video opened successfully.") # Debugging output
            threading.Thread(target=detect_faces).start()
    else:
        messagebox.showinfo("Info", "No video file selected.")

# Start the webcam
def start_webcam():
    global cap, stop_thread
    stop_thread = True
    if cap is not None:
        cap.release()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        print(f"Error: Could not open webcam.") # Debugging output
        return

    print("Webcam opened successfully.") # Debugging output
    stop_thread = False
    threading.Thread(target=detect_faces).start()


# Detect and recognize faces
def detect_faces():
    global cap, stop_thread

    while cap.isOpened() and not stop_thread:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings_frame = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings_frame):
            matches = face_recognition.compare_faces(face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = face_names[first_match_index]

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Label the face
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Resize the frame to fit the label
        resized_frame = cv2.resize(frame, (lbl_video.winfo_width(), lbl_video.winfo_height()))
        frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        root.update()

    cap.release()
    cv2.destroyAllWindows()



# Stop the detection thread
def stop_detection():
    global stop_thread
    stop_thread = True
    if cap is not None:
        cap.release()
    lbl_video.configure(image='')
    print("Detection stopped.")


# GUI Elements
lbl_video = tk.Label(root, width=30, height=30) # Set desired width or height of the video loaded
lbl_video.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_load_dataset = tk.Button(button_frame, text="Load Face Dataset", command=load_face_dataset)
btn_load_dataset.pack(side=tk.LEFT, padx=10)

btn_open_video = tk.Button(button_frame, text="Open Video", command=open_video)
btn_open_video.pack(side=tk.LEFT, padx=10)

btn_start_webcam = tk.Button(button_frame, text="Start Webcam", command=start_webcam)
btn_start_webcam.pack(side=tk.LEFT, padx=10)

btn_stop_detection = tk.Button(button_frame, text="Stop Detection", command=stop_detection)
btn_stop_detection.pack(side=tk.LEFT, padx=10)

root.mainloop()
# Update the dimensions of the video footage upon loading