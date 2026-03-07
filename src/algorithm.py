import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

import devices

# Device manager
dm = devices.Devices()

# Configure devices
dm.set_voltmeter()
dm.set_wavegen()

print(dm.get_voltage())

# # Create figure and initial display
# fig, ax = plt.subplots()
# display = np.zeros((2, 2))
# im = ax.imshow(display, cmap="binary", origin="lower", vmin=0, vmax=1)

# ax.set_title("Location of Object of Higher Resistivity")

# ax.set_xticks([0, 1])
# ax.set_yticks([0, 1])
# ax.set_xticklabels(["Left (D)", "Right (B)"])
# ax.set_yticklabels(["Bottom (C)", "Top (A)"])


# def update(frame):
#     global display

#     # Generate new voltages (replace with real sensor input if needed)
#     voltages = np.random.uniform(0.3, 1.2, 6)

#     display = np.zeros((2, 2))

#     # Decision tree
#     if voltages[1] < voltages[4]:
#         if voltages[0] > voltages[5]:
#             display[0, 1] = 1
#         else:
#             display[1, 0] = 1
#     else:
#         if voltages[2] > voltages[3]:
#             display[0, 0] = 1
#         else:
#             display[1, 1] = 1

#     im.set_data(display)
#     return [im]


# # Update every 250 ms
# ani = FuncAnimation(fig, update, interval=250, blit=True)

# plt.show()
