import threading
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Wedge

from classifier import Classifier
from simple_eit import SimpleEIT
from data_collector import object_data # For autocalibration

print("Running full Simple EIT...")

# Create the colormap for binary colors (white to black)
global_cmap = plt.cm.binary

# ========= EIT DATA THREAD =========

app = SimpleEIT()

# Shared data + synchronization
latest_data = np.zeros((2, 8))
data_lock = threading.Lock()
model_lock = threading.Lock()
stop_event = threading.Event()
pause_event = threading.Event()

state_text = None  # matplotlib text overlay

key_actions = {
    "f": lambda: clf.select_object("finger_jonah"),
    "v": lambda: clf.select_object("vertical_eraser"),
    "h": lambda: clf.select_object("horz_eraser"),
    "g": lambda: clf.select_model("gb"),
    "k": lambda: clf.select_model("knn"),
    "d": lambda: clf.select_model("lda"),
    "l": lambda: clf.select_model("logreg"),
    "m": lambda: clf.select_model("mlp"),
    "r": lambda: clf.select_model("rf"),
    "s": lambda: clf.select_model("svm"),
    "x": lambda: clf.select_model("xgb"),
}


def data_loop():
    """Data acquisition thread."""
    global latest_data
    while not stop_event.is_set():
        # Pause while user is interacting
        while pause_event.is_set() and not stop_event.is_set():
            sleep(0.05)
        with data_lock:
            data = app.run()
            # [AB_1, AB_2, AD_1, AD_2, CD_1, CD_2, BC_1, BC_2]
            # [AB_3, AB_4, AD_3, AD_4, CD_3, CD_4, BC_3, BC_4]
            latest_data = data.copy()


# Start thread
thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# ========= DISPLAY CODE =========

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
    bbox=dict(boxstyle="round,pad=0.4", facecolor="whitesmoke", edgecolor="gray")
)

# CONTROLS (centered and padded)
ax_right.text(
    0.5,
    0.45,
"""(a) Auto-calibrate object

Objects:
(f) Finger (Jonah)
(v) Vertical Eraser
(h) Horizontal Eraser

Models:
(g) GB    (k) KNN   (d) LDA
(l) LogReg (m) MLP  (r) RF
(s) SVM   (x) XGB

(e) Exit""",
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
        f"object = {clf.object_name}\nmodel = {clf.model_name}"
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


# ========= EXIT CODE =========


def on_key(event):
    global pause_event

    key = event.key
    if not key:
        return

    # EXIT
    if key == "e":
        print("Exiting...")
        stop_event.set()
        plt.close(fig)
        return

    # If valid action key → pause loop during update
    if key in key_actions:
        pause_event.set()

        try:
            print(f"Key {key} pressed -> executing action")
            key_actions[key]()
        finally:
            pause_event.clear()


# Bind key press
fig.canvas.mpl_connect("key_press_event", on_key)

# ========= START DISPLAY =========

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
