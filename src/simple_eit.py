import matplotlib.pyplot as plt
import numpy as np
from gpiozero import LED
from matplotlib.animation import FuncAnimation

import devices


class SimpleEIT:

    def __init__(self):

        # Select GPIO pins
        # MUX 1 (S+ and V+)
        self.a0_mux1 = LED(26)
        self.a1_mux1 = LED(19)

        # MUX 2 (S- and V-)
        self.a0_mux2 = LED(13)
        self.a1_mux2 = LED(6)

        # Device manager
        self.dm = devices.Devices()

        # Configure devices
        self.dm.set_voltmeter()
        self.dm.set_wavegen()

        # Create display data
        self.display = np.zeros((2, 2))

        # Create figure
        self.fig, self.ax = plt.subplots()

        self.im = self.ax.imshow(
            self.display,
            cmap="binary",
            origin="lower",
            vmin=0,
            vmax=1
        )

        self.ax.set_title("Location of Object of Higher Resistivity")

        self.ax.set_xticks([0, 1])
        self.ax.set_yticks([0, 1])
        self.ax.set_xticklabels(["Left (D)", "Right (B)"])
        self.ax.set_yticklabels(["Bottom (C)", "Top (A)"])

    def get_voltages(self):
        """
        Read voltages using the device manager and MUX control.
        """
        # Example placeholder
        return np.random.rand(6)

    def update(self, frame):

        self.display[:] = 0
        voltages = self.get_voltages()

        # Decision tree
        if voltages[1] < voltages[4]:
            if voltages[0] > voltages[5]:
                self.display[0, 1] = 1
            else:
                self.display[1, 0] = 1
        else:
            if voltages[2] > voltages[3]:
                self.display[0, 0] = 1
            else:
                self.display[1, 1] = 1

        self.im.set_data(self.display)

        return [self.im]

    def run(self):

        self.ani = FuncAnimation(
            self.fig,
            self.update,
            interval=20,
            blit=True
        )

        plt.show()


if __name__ == "__main__":
    app = SimpleEIT()
    app.run()