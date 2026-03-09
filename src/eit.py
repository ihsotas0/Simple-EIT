import datetime
import time

import numpy as np
# from gpiozero import LED

# from device_manager import DeviceManager


class SimpleEIT:

    def __init__(self):

        # GPIO controllers for multiplexers
        # MUX1 controls S+ and V+ (A0, A1)
        self.mux1 = (LED(26), LED(19))

        # MUX2 controls S- and V- (A0, A1)
        self.mux2 = (LED(13), LED(6))

        # Device manager
        self.dm = DeviceManager()

        # Configure devices
        self.dm.set_voltmeter()
        self.dm.set_wavegen()

        self.test = 0

    def get_voltages(self):
        v_return = np.zeros(6)

        # (selection for MUX 1, selection for MUX 2, voltage measurement index)
        configs = [(0, 0, 1), (0, 2, 2), (1, 2, 4), (1, 0, 3), (2, 1, 5), (3, 3, 0)]

        for s1, s2, index in configs:
            set_mux_state(self.mux1, s1)  # Apply state to mux1
            set_mux_state(self.mux2, s2)  # Apply state to mux2
            print(f"Switched MUX 1: {s1}, MUX 2: {s2}, Config: {index}")
            v_return[index] = self.dm.get_voltage()

        ct = datetime.datetime.now()

        print(f"{ct}: Measured voltages: {v_return:6f}")

        return v_return

        # return np.random.uniform(-1, 1, 6)

    def run(self):

        # Get the measured voltages
        v = self.get_voltages()

        # Compute conditionals numerically (+) for yes (-) for no. Magnitude of
        # conditional shows the "confidence" that the OHR is in that quadrant
        v_raw = np.array(
            [
                negneg((v[1] - v[4]), (v[2] - v[3])),  # display[0, 0]
                negneg((v[4] - v[1]), (v[0] - v[5])),  # display[0, 1]
                negneg((v[4] - v[1]), (v[5] - v[0])),  # display[1, 0]
                negneg((v[1] - v[4]), (v[3] - v[2])),  # display[1, 1]
            ]
        )

        # Normalize conditionals to represent a probabilty distribution
        v_norm = softmax(v_raw)

        return v_norm.reshape(2, 2)


"""Helper functions"""


def softmax(x):
    return np.exp(x - max(x)) / sum(np.exp(x - max(x)))


# HACK: If conditional is false for both cases, the output should be (-)
def negneg(x, y):
    return -(x * y) if x < 0 and y < 0 else x * y


def set_mux_state(mux, state):
    """Set mux GPIO states based on the 2-bit state."""
    # If LSB (0b01) is 1, turn on mux[0], else turn it off
    mux[0].on() if state & 0b01 else mux[0].off()
    # If second bit (0b10) is 1, turn on mux[1], else turn it off
    mux[1].on() if state & 0b10 else mux[1].off()


"""Testing"""

if __name__ == "__main__":
    # For testing
    app = SimpleEIT()
    for i in range(10):
        print(f"{i}: {app.run()}")
