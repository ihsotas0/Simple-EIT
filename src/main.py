import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from eit import *

app = SimpleEIT()

# Create figure
fig, ax = plt.subplots()

display = np.zeros([2, 2])

im = ax.imshow(display, cmap="binary", origin="lower", vmin=0, vmax=1)

ax.set_title("Confidence in Location of Object of Higher Resistivity")

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Left (D)", "Right (B)"])
ax.set_yticklabels(["Bottom (C)", "Top (A)"])

# To hold the text annotations
texts = []


def update(frame):
    data = app.run()

    # Update the image data
    im.set_data(data)

    # Remove old text annotations
    for text in texts:
        text.remove()

    # Clear the text list
    texts.clear()

    # Annotate each pixel with its value using np.ndenumerate
    for (i, j), value in np.ndenumerate(data):
        text = ax.text(j, i, f"{value:.2f}", ha="center", va="center")
        texts.append(text)

    return [im] + texts


ani = FuncAnimation(
    fig,
    update,
    interval=500,  # IMPORTANT: Update period in ms
    blit=True,
    cache_frame_data=False,
)

plt.show()
