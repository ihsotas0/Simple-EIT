from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

# # Create figure
# self.fig, self.ax = plt.subplots()

# self.im = self.ax.imshow(
#     self.display, cmap="binary", origin="lower", vmin=0, vmax=1
# )

# self.ax.set_title("Location of Object of Higher Resistivity")

# self.ax.set_xticks([0, 1])
# self.ax.set_yticks([0, 1])
# self.ax.set_xticklabels(["Left (D)", "Right (B)"])
# self.ax.set_yticklabels(["Bottom (C)", "Top (A)"])


# self.ani = FuncAnimation(
#     self.fig,
#     self.update,
#     interval=20,  # IMPORTANT: Update period in ms
#     blit=True,
#     cache_frame_data=False,
# )

# plt.show()



# def update(self, frame):

#     self.im.set_data(self.display)

#     return [self.im]