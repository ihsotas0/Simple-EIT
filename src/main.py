import os
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

# Suppress Qt/Tkinter nested event loop warning (harmless but noisy)
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

print("[Main]: Running full Simple EIT...")
global_cmap = colormaps["viridis"]  # Visible from 0.0

def gui_textbox(prompt):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        res = simpledialog.askstring("Input", prompt, parent=root)
        return res if res else "untitled"
    finally:
        root.destroy()

# ========= EIT data thread =========
app = SimpleEIT(
    scope_idn=gui_textbox("Identify oscilloscope ('DSOX'): "),
    wavegen_idn=gui_textbox("Identify wavegen ('EDU'): "),
)

latest_data = 0.5 * np.ones((2, 8))
data_lock = threading.Lock()
stop_event = threading.Event()
pause_event = threading.Event()
pause_event.set()  # Start in RUNNING state
hardware_lock = threading.Lock()  # Absolute hardware mutex

def data_loop():
    global latest_data
    while not stop_event.is_set():
        # Use timeout to periodically check stop_event without blocking indefinitely
        if not pause_event.wait(timeout=0.1):
            continue  # Still paused
            
        if stop_event.is_set():
            break
            
        acquired = hardware_lock.acquire(timeout=0.1)
        if not acquired:
            continue
            
        try:
            # Final safety check before acquiring new data
            if stop_event.is_set():
                break
            data = app.run()
            with data_lock:
                latest_data = data.copy()
        except Exception as e:
            print(f"[Main]: Data acquisition failed: {e}")
            sleep(1)
        finally:
            hardware_lock.release()
            
        if stop_event.is_set():
            break
        sleep(0.05)

thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# ========= Display setup =========
# figsize=(10,6) + width_ratios=[3,2] => Left axis is exactly 6x6 inches
fig = plt.figure(figsize=(10, 6), facecolor="#e9ecef")
fig.subplots_adjust(wspace=0.05, left=0.08, right=0.95, top=0.92, bottom=0.08)
gs = fig.add_gridspec(1, 2, width_ratios=[3, 2])

ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])

# LEFT: EIT Display
ax_left.set_title("Simple EIT Display", pad=10, fontsize=13, fontweight="bold", color="#2c3e50")
ax_left.set_xlim(-1.25, 1.25)
ax_left.set_ylim(-1.25, 1.25)
ax_left.set_aspect('equal', adjustable='box')
ax_left.axis("off")
ax_left.set_facecolor("white")

# Labels
label_radius = 1.15
for label, (x, y) in zip(
    ["A", "B", "C", "D"],
    [(0, label_radius), (label_radius, 0), (0, -label_radius), (-label_radius, 0)],
):
    ax_left.text(x, y, label, ha="center", va="center", fontsize=12, fontweight="bold", color="#34495e")

# RIGHT: Controls & Status
ax_right.axis("off")
ax_right.set_facecolor("#f8f9fa")

# Status Box - FIXED: Added explicit width to prevent character wrapping
status_text = ax_right.text(
    0.5, 0.88, "READY\nObject: None\nModel: None",
    ha="center", va="center", fontsize=11,
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#28a745", width=0.7)
)

# Instructions Box
ax_right.text(
    0.5, 0.42,
    """CONTROLS

OBJECTS
a-e: curc_a to curc_e
f: Auto-calibrate new object (<5 min)
g: Load custom object

MODELS
1: GB      2: KNN     3: LDA
4: LogReg  5: MLP     6: RF
7: SVM     8: XGB

x: EXIT""",
    ha="center", va="center", fontsize=15, family="monospace", linespacing=1.5,
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#ffffff", edgecolor="#ced4da", alpha=0.95)
)
# Geometry & Wedges
num_slices, num_rings = 8, 2
theta = 2 * np.pi / num_slices
r_outer = 1.0
r_inner = r_outer / np.sqrt(2)

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
            lw=1.2,
            edgecolor="#adb5bd",
        )
        ax_left.add_patch(global_wedges[idx])

        text_radius = (r_outer + r_inner) / 2 if ring == 0 else (r_inner + 0.1) / 2
        text_angle = start_angle + theta / 2
        x_txt, y_txt = text_radius * np.cos(text_angle), text_radius * np.sin(text_angle)
        global_texts[idx] = ax_left.text(
            x_txt, y_txt, "0.50", ha="center", va="center", fontsize=8, fontweight="bold", color="#212529"
        )

def update(frame):
    with data_lock:
        data = latest_data.copy()
    data = np.clip(data, 0, 1)

    # Box around highest probability value
    max_row, max_col = np.unravel_index(np.argmax(data), data.shape)
    max_text_idx = max_col * num_rings + max_row

    for i in range(num_slices):
        for ring in range(num_rings):
            idx = i * num_rings + ring
            value = data[ring, i]
            global_wedges[idx].set_facecolor(global_cmap(value))

            rgb = global_cmap(value)[:3]
            luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
            text_color = "white" if luminance < 0.5 else "#212529"

            global_texts[idx].set_text(f"{value:.2f}")
            global_texts[idx].set_color(text_color)

            # Clear any existing box
            global_texts[idx].set_bbox(None)

            # Apply box to the highest probability text
            if idx == max_text_idx:
                global_texts[idx].set_bbox(dict(
                    boxstyle="round,pad=0.3",
                    #facecolor="gold",
                    edgecolor="red",
                    lw=2,
                    alpha=0.0
                ))

    # Format status cleanly
    status_lines = app.get_status()
    if not status_lines:
        status_text.set_text("READY\nObject: None\nModel: None")
    else:
        status_text.set_text("ACTIVE\n" + "\n".join(status_lines))
        status_text.set_bbox(dict(boxstyle="round,pad=0.5", facecolor="#cce5ff", edgecolor="#0056b3", width=0.7))

# ========= Controls =========
def on_key(event):
    key = event.key
    if not key: return

    if key == "x":
        print("[Main]: Exiting...")
        stop_event.set()  # Signal thread to stop immediately
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
        "g": lambda f: f.set_object(gui_textbox("Set object to: ") or "untitled"),
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
        pause_event.clear()
        try:
            print(f"[Main]: Key '{key}' pressed, executing action...")
            status_text.set_text("  BUSY\nExecuting command...\n(Data paused)")
            status_text.set_bbox(dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffc107", width=0.7))
            fig.canvas.draw_idle()

            with hardware_lock:
                key_actions[key](app)
                
        except Exception as e:
            print(f"[Main]: Action '{key}' failed: {e}")
        finally:
            pause_event.set()
            fig.canvas.draw_idle()

fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.draw()
ani = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)
plt.show()