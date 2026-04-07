import threading
from functools import partial
from time import sleep  # TESTING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Wedge

import classifiers as cf
from simple_eit import SimpleEIT

print("Running full Simple EIT...")

# ========= USER INPUT =========

# Get classifier
# List only callable, non-dunder functions
functions = [
    name
    for name in dir(cf)
    if callable(getattr(cf, name)) and not name.startswith("__")
]

print(f"List of classifiers: {functions}")

cf_in = input("Choose classifier by function name: ")

if cf_in not in functions:
    raise RuntimeError("Classifier does not exist!")

# Get object
print(f"List of objects: {cf.OBJECTS}")

obj_in = input("Choose object by name: ")

if obj_in not in cf.OBJECTS:
    raise RuntimeError("Object does not exist!")

# Get cmap
print(f"Recommended: ['binary']")

colors = input("Choose cmap: ")

if colors not in colormaps:
    raise RuntimeError("Colormap does not exist!")

# Create the colormap for binary colors (white to black)
global_cmap = getattr(plt.cm, colors)


# ========= EIT DATA THREAD =========

# Some functional magic (even better)
# app = SimpleEIT(partial(getattr(cf, cf_in), obj=obj_in))  # NOT TESTING

# Shared data + synchronization
latest_data = np.zeros((2, 8))
data_lock = threading.Lock()
stop_event = threading.Event()


# Data acquisition thread
def data_loop():
    global latest_data
    while not stop_event.is_set():
        # app.run() # NOT TESTING
        # rand_vec = np.random.random((2, 8))**8  # TESTING
        # data = cf.mse_lut(rand_vec, obj="testing")  # TESTING
        # data = rand_vec / rand_vec.sum()  # TESTING
        data = np.array([[0.24, 0.2, 0.05, 0, 0, 0, 0, 0], [0.1, 0.4, 0.01, 0, 0, 0, 0, 0]]) # TESTING
        sleep(0.5)  # TESTING
        with data_lock:
            # [AB_1, AB_2, AD_1, AD_2, CD_1, CD_2, BC_1, BC_2]
            # [AB_3, AB_4, AD_3, AD_4, CD_3, CD_4, BC_3, BC_4]
            latest_data = data.copy()


# Start thread
thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# ========= DISPLAY CODE =========

fig, ax = plt.subplots(figsize=(6, 6))

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
    ax.text(x, y, label, ha="center", va="center", fontsize=12, fontweight="bold")

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


# Function to update the wedges and text for animation
def update(frame):
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

    # Set plot settings
    ax.axis("equal")
    ax.axis("off")

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
    ax.add_patch(wedge)
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

    text_obj = ax.text(
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
    """Key press handler (ends thread)"""
    print("Key pressed, exiting...")

    # Signal thread to stop
    stop_event.set()
    thread.join(timeout=1)

    # app.close() # NOT TESTING
    plt.close(fig)
    print("Done!")


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
