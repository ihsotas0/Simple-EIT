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

# Use a more visible colormap initially. 'binary' maps 0->white, which is invisible on white backgrounds.
global_cmap = colormaps["viridis"] 

def gui_textbox(prompt):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        return simpledialog.askstring("Input", prompt)
    finally:
        root.destroy()

# ========= EIT data thread =========
app = SimpleEIT(
    scope_idn=gui_textbox("Identify oscilloscope: "),
    wavegen_idn=gui_textbox("Identify wavegen: "),
)

latest_data = 0.5 * np.ones((2, 8))  # Start with mid-values so shapes are visible immediately
data_lock = threading.Lock()
stop_event = threading.Event()
pause_event = threading.Event()
pause_event.set()  # Start in RUNNING state

def data_loop():
    global latest_data
    while not stop_event.is_set():
        pause_event.wait()  # Blocks only when pause_event is cleared
        try:
            data = app.run()
            with data_lock:
                latest_data = data.copy()
        except Exception as e:
            print(f"[Main]: Data acquisition failed: {e}")
            sleep(1)
        sleep(0.05)  # Prevent 100% CPU usage while waiting

thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# ========= Display setup =========
fig = plt.figure(figsize=(10, 8), facecolor="lightgray")
fig.subplots_adjust(wspace=0.25, left=0.05, right=0.98, top=0.90, bottom=0.05)
gs = fig.add_gridspec(1, 2, width_ratios=[2, 1])

ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])

ax_left.set_title("Simple EIT Display", pad=16, fontsize=13, fontweight="bold")
ax_right.set_title("Controls and Status", pad=16, fontsize=13, fontweight="bold")

# FIX: Explicit limits prevent clipping of outer labels and wedges
ax_left.set_xlim(-1.25, 1.25)
ax_left.set_ylim(-1.25, 1.25)
ax_left.axis("off")
ax_left.set_facecolor("white")
ax_right.axis("off")

# Labels
label_radius = 1.15
for label, (x, y) in zip(
    ["A", "B", "C", "D"],
    [(0, label_radius), (label_radius, 0), (0, -label_radius), (-label_radius, 0)],
):
    ax_left.text(x, y, label, ha="center", va="center", fontsize=12, fontweight="bold")

# Geometry
num_slices, num_rings = 8, 2
theta = 2 * np.pi / num_slices
r_outer = 1.0
r_inner = r_outer / np.sqrt(2)

# Pre-create artists
global_wedges = [None] * (num_slices * num_rings)
global_texts = [None] * (num_slices * num_rings)

for i in range(num_slices):
    start_angle = i * theta
    for ring in range(num_rings):
        idx = i * num_rings + ring
        radius = r_outer if ring == 0 else r_inner
        global_wedges[idx] = Wedge(
            center=(0, 0),
            r=radius,
            theta1=np.degrees(start_angle),
            theta2=np.degrees(start_angle + theta),
            facecolor=global_cmap(0.5),
            lw=1,
            edgecolor="gray",
        )
        ax_left.add_patch(global_wedges[idx])

        text_radius = (r_outer + r_inner) / 2 if ring == 0 else (r_inner + 0.1) / 2
        text_angle = start_angle + theta / 2
        x_txt, y_txt = text_radius * np.cos(text_angle), text_radius * np.sin(text_angle)
        global_texts[idx] = ax_left.text(
            x_txt, y_txt, "0.50", ha="center", va="center", fontsize=8, fontweight="bold"
        )

# Status text
status_text = ax_right.text(
    0.5,
    0.88,
    "object = \nmodel = ",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="whitesmoke", edgecolor="gray"),
)

# Instructions
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
    with data_lock:
        data = latest_data.copy()

    # Clamp values to [0, 1] for safe colormap indexing
    data = np.clip(data, 0, 1)

    for i in range(num_slices):
        for ring in range(num_rings):
            idx = i * num_rings + ring
            value = data[ring, i]
            global_wedges[idx].set_facecolor(global_cmap(value))
            text_color = "black" if value < 0.5 else "white"
            global_texts[idx].set_text(f"{value:.2f}")
            global_texts[idx].set_color(text_color)

    status_text.set_text(app.get_status())

# ========= Controls =========
def on_key(event):
    key = event.key
    if not key:
        return

    if key == "x":
        print("[Main]: Exiting...")
        stop_event.set()
        app.close()
        thread.join(timeout=2)
        plt.close(fig)
        return

    key_actions = {
        "a": lambda f: f.set_object("curc_a"),
        "b": lambda f: f.set_object("curc_b"),
        "c": lambda f: f.set_object("curc_c"),
        "d": lambda f: f.set_object("curc_d"),
        "e": lambda f: f.set_object("curc_e"),
        "f": lambda f: f.auto_calibration(gui_textbox("New object name: ") or "untitled", n=10),
        "g": lambda f: f.set_object(gui_textbox("Set object to (prepend 'auto_cal_' for new objects): ") or "untitled"),
        "1": lambda f: f.set_model("gb"),
        "2": lambda f: f.set_model("knn"),
        "3": lambda f: f.set_model("lda"),
        "4": lambda f: f.set_model("logreg"),
        "5": lambda f: f.set_model("mlp"),
        "6": lambda f: f.set_model("rf"),
        "7": lambda f: f.set_model("svm"),
        "8": lambda f: f.set_model("xgb"),
    }

    if key in key_actions:
        pause_event.clear()  # PAUSE acquisition before changing state
        try:
            print(f"[Main]: Key '{key}' pressed, executing action...")
            key_actions[key](app)
        except Exception as e:
            print(f"[Main]: Action '{key}' failed: {e}")
        finally:
            pause_event.set()  # RESUME acquisition

fig.canvas.mpl_connect("key_press_event", on_key)

# ========= Start =========
# Force initial render so shapes/text appear before first animation frame
fig.canvas.draw()
ani = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)
plt.show()