import datetime
import time

import numpy as np
from gpiozero import LED

from device_manager import DeviceManager


class SimpleEIT:

    def __init__(self):

        # GPIO controllers for multiplexers
        # MUX1 controls S+ and V+ (A0, A1)
        self.mux1 = (LED(19), LED(26))

        # MUX2 controls S- and V- (A0, A1)
        self.mux2 = (LED(6), LED(13))

        # Turns MUXs off before switching and on again
        self.mux_toggle = (LED(5), LED(16))

        # Device manager
        self.dm = DeviceManager()

        # Configure devices
        self.dm.initialize_voltmeter()
        self.dm.set_voltmeter()
        self.dm.set_wavegen()

        # self.test = 0

    def get_voltages(self):
        v_return = np.zeros(6)

        # (selection for MUX 1, selection for MUX 2, voltage measurement index)
        configs = [
            (4, 4, 1),
            (1, 3, 2),
            (2, 1, 3),
            (3, 2, 4),
            (1, 1, 5),
            (2, 3, 6),
        ]

        for s1, s2, index in configs:
            
            # Start MUX switch (ground measurement leads)
            self.mux_toggle[0].off()
            self.mux_toggle[1].off()

            # Switch MUX state
            set_mux_state(self.mux1, s1)  # Apply state to mux1
            set_mux_state(self.mux2, s2)  # Apply state to mux2
            print(f"Switched MUX 1: S{s1}, MUX 2: S{s2}, Config: {index}")
            
            # End MUX switch (turn measurement leads on)
            self.mux_toggle[0].on()
            self.mux_toggle[1].on()
            
            # Get voltage, assign to index (V_AB, V_AD, V_BC, V_CD, V_AC, V_BD)
            v_return[index - 1] = self.dm.get_voltage()

        ct = datetime.datetime.now()

        print(f"{ct}: Measured voltages: {v_return}")

        return v_return

        # return np.random.uniform(-1, 1, 6)

    def run(self):

        # Get the measured voltages
        # (V_AB, V_AD, V_BC, V_CD, V_AC, V_BD)
        v = self.get_voltages()

        # Compute conditionals numerically (+) for yes (-) for no. Magnitude of
        # conditional shows the "confidence" that the OHR is in that quadrant
        # v_raw = np.array(
        #     [
        #         negneg((v[] - v[]), (v[] - v[])),  # display[0, 0]
        #         negneg((v[] - v[]), (v[] - v[])),  # display[0, 1]
        #         negneg((v[] - v[]), (v[] - v[])),  # display[1, 0]
        #         negneg((v[] - v[]), (v[] - v[])),  # display[1, 1]
        #     ]
        # )

        index = np.argsort(arr[:4])[-2]

        v_norm = np.zeros(4)
        v_norm[index] = 1

        # Normalize conditionals to represent a probability distribution
        v_norm = softmax(v_raw)

        # Matrix represents this:
        #
        #  AD   AB
        #  CD   BC
        #

        return v_norm.reshape(2, 2)

# Helper functions

def softmax(x):
    return np.exp(x - max(x)) / sum(np.exp(x - max(x)))

def set_mux_state(mux, state):
    """Set mux GPIO states based on the 2-bit state."""
    match state:
        case 1:
            mux[0].off()
            mux[1].off()
        case 2:
            mux[0].on()
            mux[1].off()
        case 3:
            mux[0].off()
            mux[1].on()
        case 4:
            mux[0].on()
            mux[1].on()


# Testing
if __name__ == "__main__":
    # For testing
    app = SimpleEIT()
    for i in range(10):
        print(f"{i}: {app.run()}")
