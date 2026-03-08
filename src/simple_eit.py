import datetime
import matplotlib.pyplot as plt
import numpy as np
from gpiozero import LED
from matplotlib.animation import FuncAnimation

import devices


class SimpleEIT:

    def __init__(self):

        # GPIO controllers for multiplexers
        # MUX1 controls S+ and V+ (A1, A0)
        self.mux1 = (LED(26), LED(19))

        # MUX2 controls S- and V- (A1, A0)
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
            self.display, cmap="binary", origin="lower", vmin=0, vmax=1
        )

        self.ax.set_title("Location of Object of Higher Resistivity")

        self.ax.set_xticks([0, 1])
        self.ax.set_yticks([0, 1])
        self.ax.set_xticklabels(["Left (D)", "Right (B)"])
        self.ax.set_yticklabels(["Bottom (C)", "Top (A)"])

    def get_voltages(self):
        v_return = np.zeros(6)
        # (selection for MUX 1, selection for MUX 2, voltage measurement index)
        configs = [(0, 0, 1), (0, 2, 2), (1, 2, 4), (1, 0, 3), (2, 1, 5), (3, 3, 0)]

        for mux1, mux2, index in configs:
            self.set_mux(mux1, mux2)
            v_return[index] = self.dm.get_voltage()

        ct = datetime.datetime.now()

        print(f"{ct}: {v_return}")

        return v_return

    def set_mux(self, c1, c2):
        """Controls selections for MUX 1 and MUX 2 using GPIO"""

        def set_mux_state(mux, state):
            mux[0].off() if state & 0b01 == 0 else mux[0].on()
            mux[1].off() if state & 0b10 == 0 else mux[1].on()

        set_mux_state(self.mux1, c1)
        set_mux_state(self.mux2, c2)

    def update(self, frame):

        self.im.set_data(self.display)

        return [self.im]

    def run(self):

        self.ani = FuncAnimation(
            self.fig,
            self.update,
            interval=20,  # IMPORTANT: Update period in ms
            blit=True,
            cache_frame_data=False,
        )

        plt.show()
        
        try:
            while True:
                # Get the measured voltages
                voltages = self.get_voltages()

                # Compute conditionals numerically (+) for yes (-) for no. Magnitude of
                # conditional shows the "confidence" that the OHR is in that quadrant
                v_raw = np.array([
                    negneg((v[1] - v[4]), (v[2] - v[3])),  # self.display[0, 0]
                    negneg((v[4] - v[1]), (v[0] - v[5])),  # self.display[0, 1]
                    negneg((v[4] - v[1]), (v[5] - v[0])),  # self.display[1, 0]
                    negneg((v[1] - v[4]), (v[3] - v[2])),  # self.display[1, 1]
                ])

                # Normalize conditionals to represent a probabilty distribution
                v_norm = softmax(v_raw)

                self.display = v_norm.reshape(2, 2)

        except KeyboardInterrupt:
            pass


def softmax(x):
    return np.exp(x - max(x)) / sum(np.exp(x - max(x)))


# HACK: If conditional is false for both cases, the output should be (-)
def negneg(x, y):
    return -(x*y) if x < 0 and y < 0 else x*y


if __name__ == "__main__":
    app = SimpleEIT()
    app.run()
