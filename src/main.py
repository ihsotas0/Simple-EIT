import threading

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

import classifiers as cf
from simple_eit import SimpleEIT

print("Running full Simple EIT...")

# List classifiers, kinda lazy but it works
print(dir(cf))
cf_in = input("Choose classifier by function name: ")

# No try/catch, just type the function correctly please :)
app = SimpleEIT(getattr(cf, cf_in))

# Shared data + synchronization
latest_data = np.zeros((2, 2))
data_lock = threading.Lock()
stop_event = threading.Event()


# Data acquisition thread
def data_loop():
    global latest_data
    while not stop_event.is_set():
        data = app.run()
        with data_lock:
            latest_data = data.copy()


# Start thread
thread = threading.Thread(target=data_loop, daemon=True)
thread.start()

# Plot setup
fig, ax = plt.subplots()

im = ax.imshow(latest_data, cmap="binary", origin="lower", vmin=0, vmax=1)

ax.set_title("Confidence in OHR Location")
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Left (D)", "Right (B)"])
ax.set_yticklabels(["Bottom (C)", "Top (A)"])

texts = []


# Animation update
def update(frame):
    with data_lock:
        data = latest_data.copy()

    im.set_data(data)

    # Remove old text
    for text in texts:
        text.remove()
    texts.clear()

    # Assign new probabilites to texts
    for (i, j), value in np.ndenumerate(data):
        text = ax.text(j, i, f"{value:.2f}", ha="center", va="center")
        texts.append(text)

    return [im] + texts


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

ani = FuncAnimation(
    fig,
    update,
    interval=100,
    blit=True,
    cache_frame_data=False,
)

plt.show()
