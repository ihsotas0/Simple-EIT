import numpy as np
from gpiozero import LED

from device_manager import DeviceManager


class SimpleEIT:

    def __init__(self, model):

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

        # Classification model
        self.model = model

    def get_voltages(self):
        v_return = np.zeros(6)

        # (selection for MUX 1, selection for MUX 2, voltage measurement index)
        configs = [
            (4, 4, 1),
            (1, 3, 2),
            (2, 1, 3),
            (3, 2, 4),
            (1, 1, 5),  # Diag: Not needed for 2nd highest method
            (2, 3, 6),  # Diag
        ]

        for s1, s2, index in configs:

            # Start MUX switch (ground measurement leads)
            self.mux_toggle[0].off()
            self.mux_toggle[1].off()

            # Switch MUX state
            self._set_mux_state(self.mux1, s1)  # Apply state to mux1
            self._set_mux_state(self.mux2, s2)  # Apply state to mux2
            print(f"Switched MUX 1: S{s1}, MUX 2: S{s2}, Config: {index}")

            # End MUX switch (turn measurement leads on)
            self.mux_toggle[0].on()
            self.mux_toggle[1].on()

            # Get voltage, assign to index
            # (V_AB, V_AD, V_BC, V_CD, V_AC, V_BD)
            v_return[index - 1] = self.dm.get_voltage()

        print(f"Measured voltages: {v_return}")

        return v_return

    def run(self):

        # Get the measured voltages
        # (V_AB, V_AD, V_BC, V_CD, V_AC, V_BD)
        v = self.get_voltages()

        # Use classifier
        v_raw = self.model(v)

        # Normalize to represent probability distribution
        v_norm = softmax(v_raw)

        # Matrix OHR locations:
        # [AD AB]
        # [CD BC]

        return v_norm.reshape(2, 2)

    # Context Manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self.dm.close()

    # Helper functions

    def _set_mux_state(mux, state):
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
