import time 
from tkinter import messagebox
import threading

def startanalysis():

    # Global dictionary to store minute counts    
    minute_counts = {}
    tracking_active = True

    def track_minute_counts():
        """Track the minute counts in a background thread."""
        global minute_counts, tracked_ids, tracking_active
        while tracking_active:
            # Get the current hour in HH:MM format
            current_minute = time.strftime("%Y-%m-%d %H:%M")

            # Add/update the count of unique tracked IDs for this hour
            minute_counts[current_minute] = len(tracked_ids)

            # Sleep until the next hour
            current_time = time.time()
            next_minute = (int(current_time // 60) + 1) * 60
            time.sleep(max(0, next_minute - current_time))

    def display_minute_counts():
        """Display the stored minute counts."""
        if not minute_counts:
            messagebox.showinfo("Minute Counts", "No data recorded yet.")
            return

        counts_str = "\n".join([f"{minute}: {count} people" for minute, count in sorted(minute_counts.items())])
        messagebox.showinfo("Minute Counts", f"Minute People Counts:\n\n{counts_str}")

    # Start the minute tracking in a separate thread
    minute_thread = threading.Thread(target=track_minute_counts, daemon=True)
    minute_thread.start()

