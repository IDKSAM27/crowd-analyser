import matplotlib.pyplot as plt
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def show_graph(minute_counts, graph_type="line"):
    """
    Display a line or bar graph for minute counts in a new Tkinter window.

    Args:
        minute_counts (dict): A dictionary with minutes as keys and counts as values.
        graph_type (str): Type of graph to display, either 'line' or 'bar'. Defaults to 'line'.
    """
    # Create a new top-level Tkinter window
    graph_window = Toplevel()
    graph_window.title("Minute Counts Graph")
    graph_window.geometry("800x600")
    
    # Sort the minute counts by time for proper display
    sorted_minutes = sorted(minute_counts.keys())
    counts = [minute_counts[minute] for minute in sorted_minutes]

    # Create the figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    if graph_type == "line":
        ax.plot(sorted_minutes, counts, marker='o', label="People Count")
    elif graph_type == "bar":
        ax.bar(sorted_minutes, counts, label="People Count", color='blue', alpha=0.7)

    # Configure the graph
    ax.set_title("People Count Per Minute")
    ax.set_xlabel("Time (Minute)")
    ax.set_ylabel("People Count")
    ax.set_xticks(range(len(sorted_minutes)))
    ax.set_xticklabels(sorted_minutes, rotation=45, ha="right", fontsize=8)
    ax.legend()
    ax.grid(True)

    # Embed the figure into the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Add a close button
    btn_close = tk.Button(graph_window, text="Close", command=graph_window.destroy)
    btn_close.pack(pady=10)
