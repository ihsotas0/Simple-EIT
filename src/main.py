import threading
from functools import partial
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Wedge

import classifiers as cf
from simple_eit import SimpleEIT

print("Running full Simple EIT...")

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

print(f"List of objects: {cf.OBJECTS}")

obj_in = input("Choose object by name: ")

if obj_in not in cf.OBJECTS:
    raise RuntimeError("Object does not exist!")

print(f"Recommended: ['binary']")

colors = input("Choose cmap: ")

if colors not in colormaps:
    raise RuntimeError("Colormap does not exist!")

# Create the colormap for binary colors (white to black)
cmap = getattr(plt.cm, colors)

# Some functional magic (even better)
# app = SimpleEIT(partial(getattr(cf, cf_in), obj=obj_in))

# Shared data + synchronization
latest_data = np.zeros((2, 8))
data_lock = threading.Lock()
stop_event = threading.Event()


# Data acquisition thread
def data_loop():
    global latest_data
    while not stop_event.is_set():
        # app.run()
        data = np.random.random((2, 8))
        sleep(0.5)
        with data_lock:
            latest_data = data.copy()


# Start thread
thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# Plot setup
fig, ax = plt.subplots(figsize=(6, 6))

# Add labels A, B, C, D around the plot
label_radius = 1.1
ax.text(0, label_radius, "A", ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(label_radius, 0, "B", ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(0, -label_radius, "C", ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(-label_radius, 0, "D", ha="center", va="center", fontsize=12, fontweight="bold")

# Number of slices and rings
num_slices = 8
num_rings = 2

# Define angle range per slice
theta = 2 * np.pi / num_slices

# Calculate the inner radius for the split
r_outer = 1
r_inner = r_outer / np.sqrt(2)

# Initialize patches and text objects
wedges = [None] * (num_slices * num_rings)
texts = [None] * (num_slices * num_rings)


# Function to update the wedges and text
def update(frame):
    with data_lock:
        data = latest_data.copy()

    print(f"Data at frame {frame}: {data}")

    for i in range(num_slices):
        start_angle = i * theta

        for ring in range(num_rings):
            index = i * num_rings + ring
            value = data[ring, i]
            color_intensity = value

            # Update or create new wedges if needed
            if wedges[index] is None:
                radius = r_outer if ring == 0 else r_inner

                # Create a new wedge
                wedge = Wedge(
                    center=(0, 0),
                    r=radius,
                    theta1=np.degrees(start_angle),
                    theta2=np.degrees(start_angle + theta),
                    facecolor=cmap(color_intensity),
                    lw=0,
                    alpha=0.8,
                )

                ax.add_patch(wedge)
                wedges[index] = wedge
            else:
                # Update existing wedge
                wedges[index].set_facecolor(cmap(color_intensity))

            # Update text
            text_radius = (r_outer + r_inner) / 2 if ring == 0 else (r_inner + 0.1) / 2
            text_angle = (start_angle + start_angle + theta) / 2
            x_text = text_radius * np.cos(text_angle)
            y_text = text_radius * np.sin(text_angle)

            text_color = "black" if color_intensity < 0.5 else "white"
            if texts[index] is None:
                # Create a new text object
                text_obj = ax.text(
                    x_text,
                    y_text,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=text_color,
                )
                texts[index] = text_obj
            else:
                # Update the existing text object
                texts[index].set_position((x_text, y_text))
                texts[index].set_text(f"{value:.2f}")
                texts[index].set_color(text_color)

    # Set the aspect ratio to be equal
    ax.axis("equal")
    ax.axis("off")

    return []


# Key press handler (ends thread)
def on_key(event):
    print("Key pressed, exiting...")

    # Signal thread to stop
    stop_event.set()
    thread.join(timeout=1)

    app.close()
    plt.close(fig)


# Bind key press
fig.canvas.mpl_connect("key_press_event", on_key)

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
