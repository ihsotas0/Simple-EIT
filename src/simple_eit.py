import matplotlib.pyplot as plt
import numpy as np
from gpiozero import LED
from matplotlib.animation import FuncAnimation

import devices


class SimpleEIT:

    def __init__(self):

        # GPIO controllers for multiplexers
        # MUX1 controls S+ and V+ (A0, A1)
        self.mux1 = (LED(26), LED(19))

        # MUX2 controls S- and V- (A0, A1)
        self.mux2 = (LED(13), LED(6))

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

        self.set_mux(0, 0)
        
        return np.random.rand(6)

    def set_mux(self, c1, c2)
        """ Controls selections for MUX 1 and MUX 2 using GPIO"""
        match c1:
            case 0:
            case 1:
            case 2:
            case 3:
        match c2:
            case 0:
            case 1:
            case 2:
            case 3:

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
            blit=True,
            cache_frame_data=False
        )

        plt.show()


if __name__ == "__main__":
    app = SimpleEIT()
    app.run()