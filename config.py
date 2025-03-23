import json
import tkinter as tk
from tkinter import messagebox
# from head import restart_app

def restart_app():
    from head import restart_app
    restart_app()

def load_config():
    # Load the configuration from config.json
    try:
        with open ("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration if file doesn't exist
        return {
            "process_interval": 10,
            "iou_threshold": 0.3,
            "max_age": 20,
            "min_hits": 3,
            "alarm_threshold": 250,
            "alarm_interval": 10,
            "roi_default": [0, 0, 640, 480]
        }
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in config.json")
        return{}
    
def save_config(config, editor=None):
    # Save the updated configuration to config.json
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        messagebox.showinfo("Success", "Configuration saved successfully.")
        if editor:
            # Close the editor
            editor.destroy()  
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")  

def open_config_editor(root, config):
    # Open a GUI window to edit the configuration
    editor = tk.Toplevel(root)
    editor.title("Edit Configuration")
    editor.geometry("280x250")

    # Create input fields for each configuration parameter
    def add_field(row, label, key, default):
        tk.Label(editor, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Entry(editor)
        entry.insert(0, config.get(key, default))
        entry.grid(row=row, column=1, padx=10, pady=5)
        return entry

    entries = {
        "process_interval": add_field(0, "Process Interval:", "process_interval", 10),
        "iou_threshold": add_field(1, "IOU Threshold:", "iou_threshold", 0.3),
        "max_age": add_field(2, "Max Age:", "max_age", 20),
        "min_hits": add_field(3, "Min Hits:", "min_hits", 3),
        "alarm_threshold": add_field(4, "Alarm Threshold:", "alarm_threshold", 250),
        "alarm_interval": add_field(5, "Alarm Interval (sec):", "alarm_interval", 10),
    }

    def save_changes():
        updated_config = {}
        for key, entry in entries.items():
            value = entry.get()
            try:
                if "." in value:  # Convert to float if it contains a decimal point
                    updated_config[key] = float(value)
                else:
                    updated_config[key] = int(value)  # Convert to int otherwise
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {key}: {value}")
                return
        save_config(updated_config, editor)
        restart_app()


    # Save button
    btn_save = tk.Button(editor, text="Save", command=save_changes)
    btn_save.grid(row=6, column=0, columnspan=2, pady=10)

    editor.transient(root)
    editor.grab_set()