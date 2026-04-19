import threading
from time import sleep

import tkinter as tk
from tkinter import simpledialog

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Wedge

from simple_eit import SimpleEIT

print("[Main]: Running full Simple EIT...")

# Create the colormap for binary colors (white to black)
global_cmap = plt.cm.binary

# ========= EIT data thread =========

app = SimpleEIT()

# Shared data + synchronization
latest_data = np.zeros((2, 8))
data_lock = threading.Lock()
model_lock = threading.Lock()
stop_event = threading.Event()
pause_event = threading.Event()


def data_loop():
    global latest_data
    while not stop_event.is_set():
        while pause_event.is_set() and not stop_event.is_set():
            sleep(1)
        try:
            with data_lock:
                data = app.run()
                latest_data = data.copy()
        except Exception as e:
            print(f"[Main]: Data acquisition failed: {e}")
            sleep(1)  # Back off before retrying


# Start thread
thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# ========= Display code =========

fig = plt.figure(figsize=(10, 8))
fig.subplots_adjust(wspace=0.25, left=0.05, right=0.98, top=0.90, bottom=0.05)
gs = fig.add_gridspec(1, 2, width_ratios=[2, 1])

ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])

ax_left.set_title("Simple EIT Display", pad=16, fontsize=13, fontweight="bold")
ax_right.set_title("Controls and Status", pad=16, fontsize=13, fontweight="bold")

# Add labels A, B, C, D around the plot
label_radius = 1.1
labels = ["A", "B", "C", "D"]
label_positions = [
    (0, label_radius),
    (label_radius, 0),
    (0, -label_radius),
    (-label_radius, 0),
]
for label, (x, y) in zip(labels, label_positions):
    ax_left.text(x, y, label, ha="center", va="center", fontsize=12, fontweight="bold")

# Number of slices and rings
num_slices = 8
num_rings = 2

# Define angle range per slice
theta = 2 * np.pi / num_slices

# Calculate the inner radius for the split
r_outer = 1
r_inner = r_outer / np.sqrt(2)

# Initialize patches and text objects
global_wedges = [None] * (num_slices * num_rings)
global_texts = [None] * (num_slices * num_rings)
status_text = None

ax_right.set_xlim(0, 1)
ax_right.set_ylim(0, 1)
ax_right.axis("off")

# STATUS (top box)
status_text = ax_right.text(
    0.5,
    0.88,
    "",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="whitesmoke", edgecolor="gray"),
)

# CONTROLS (centered and padded)
ax_right.text(
    0.5,
    0.45,
    """Objects:
(a-e) curc_a to curc_e
(f) Run auto-calibration of new object
(g) Other, input object name

Models:
(1) GB        (2) KNN    (3) LDA
(4) LogReg    (5) MLP    (6) RF
(7) SVM (recommended)    (8) XGB

(x) Exit""",
    ha="center",
    va="center",
    fontsize=11,
    family="monospace",
    linespacing=1.4,
)


def update(frame):
    """Function to update the wedges and text for animation."""
    with data_lock:
        data = latest_data.copy()

    # Update wedges and texts
    for i in range(num_slices):
        start_angle = i * theta
        for ring in range(num_rings):
            index = i * num_rings + ring
            value = data[ring, i]
            color_intensity = value
            text_color = "black" if value < 0.5 else "white"

            # Update or create wedge and text
            update_or_create(
                index, i, ring, start_angle, value, color_intensity, text_color
            )

    status_text.set_text(
        f"object = {app.classifier.object_name}\nmodel = {app.classifier.model_name}"
    )

    # Set plot settings
    ax_left.axis("equal")
    ax_left.axis("off")
    ax_right.axis("off")

    return []


def update_or_create(
    index, slice_index, ring, start_angle, value, color_intensity, text_color
):
    """A unified function to update or create both wedges and text objects."""
    if global_wedges[index] is None:
        # Create wedge if it doesn't exist
        radius = r_outer if ring == 0 else r_inner
        create_wedge(index, slice_index, ring, start_angle, radius, color_intensity)

    else:
        # Update existing wedge
        update_existing_wedge(index, color_intensity)

    if global_texts[index] is None:
        # Create text if it doesn't exist
        create_text(index, slice_index, ring, start_angle, value, text_color)
    else:
        # Update existing text
        update_existing_text(index, value, text_color)


def create_wedge(index, slice_index, ring, start_angle, radius, color_intensity):
    """Creates a wedge object."""
    wedge = Wedge(
        center=(0, 0),
        r=radius,
        theta1=np.degrees(start_angle),
        theta2=np.degrees(start_angle + theta),
        facecolor=global_cmap(color_intensity),
        lw=0,
    )
    ax_left.add_patch(wedge)
    global_wedges[index] = wedge


def update_existing_wedge(index, color_intensity):
    """Updates the color of an existing wedge."""
    global_wedges[index].set_facecolor(global_cmap(color_intensity))


def create_text(index, slice_index, ring, start_angle, value, text_color):
    """Creates a text label object."""
    text_radius = (r_outer + r_inner) / 2 if ring == 0 else (r_inner + 0.1) / 2
    text_angle = (start_angle + start_angle + theta) / 2
    x_text = text_radius * np.cos(text_angle)
    y_text = text_radius * np.sin(text_angle)

    text_obj = ax_left.text(
        x_text,
        y_text,
        f"{value:.2f}",
        ha="center",
        va="center",
        fontsize=8,
        color=text_color,
    )
    global_texts[index] = text_obj


def update_existing_text(index, value, text_color):
    """Updates an existing text object."""
    global_texts[index].set_text(f"{value:.2f}")
    global_texts[index].set_color(text_color)


# ========= User input and exit code =========


key_actions = {
    "a": lambda f: f.set_object("curc_a"),  # Premade objects
    "b": lambda f: f.set_object("curc_b"),
    "c": lambda f: f.set_object("curc_c"),
    "d": lambda f: f.set_object("curc_d"),
    "e": lambda f: f.set_object("curc_e"),
    "f": lambda f: f.auto_calibration(gui_object_name(), n=10),  # Make new object data
    "g": lambda f: f.set_object(gui_object_name()),  # Load new object from text input
    "1": lambda f: f.set_model("gb"),  # Models to select for classification
    "2": lambda f: f.set_model("knn"),
    "3": lambda f: f.set_model("lda"),
    "4": lambda f: f.set_model("logreg"),
    "5": lambda f: f.set_model("mlp"),
    "6": lambda f: f.set_model("rf"),
    "7": lambda f: f.set_model("svm"),
    "8": lambda f: f.set_model("xgb"),
}


def gui_object_name():
    root = tk.Tk()
    root.withdraw()

    answer = simpledialog.askstring("Input", "Object Name:")
    return answer


def on_key(event):
    global pause_event

    key = event.key
    if not key:
        return

    # End program
    if key == "e":
        print("[Main]: Exiting...")
        stop_event.set()
        app.close()
        plt.close(fig)
        return

    # If valid action key, then pause loop during runtime of function
    if key in key_actions:
        pause_event.set()

        try:
            print(f"[Main]: Key {key} pressed, executing action...")
            key_actions[key](app)
        finally:
            pause_event.clear()


# Bind key press
fig.canvas.mpl_connect("key_press_event", on_key)

# ========= Start display =========

# Animation setup
ani = FuncAnimation(
    fig,
    update,
    interval=400,
    blit=True,
    cache_frame_data=False,
)

# Display the plot
plt.show()
plt.tight_layout()
