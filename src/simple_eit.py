import csv
from datetime import datetime
from pathlib import Path

import numpy as np
from gpiozero import LED

# import data_collector as dc  # For autocalibration
from classifier import Classifier
from device_manager import DeviceManager

# To ensure classifier is initialized correctly
DEFAULT_OBJECT = "curc_a"
DEFAULT_MODEL = "svm"

# Default scope and wavegen identifiers
DEFAULT_SCOPE_IDN = "KEYSIGHT"
DEFAULT_WAVEGEN_IDN = "AGILENT"

# GPIO pin defaults
DEFAULT_MUX1_PINS = (19, 26)
DEFAULT_MUX2_PINS = (6, 13)
DEFAULT_MUX_TOGGLE_PINS = (5, 16)

# Auto-cal HACK
DATA_DIR = Path("..") / "data"


class SimpleEIT:
    """Wrapper for Simple EIT instrument control."""

    def __init__(
        self,
        object_name=DEFAULT_OBJECT,
        model_name=DEFAULT_MODEL,
        scope_idn=DEFAULT_SCOPE_IDN,
        wavegen_idn=DEFAULT_WAVEGEN_IDN,
        mux1_pins=DEFAULT_MUX1_PINS,
        mux2_pins=DEFAULT_MUX2_PINS,
        mux_toggle=DEFAULT_MUX_TOGGLE_PINS,
    ):
        """Pick initial classifier and frequency."""

        # GPIO controllers for multiplexers
        # MUX1 controls S+ and V+ (A0, A1)
        self.mux1 = tuple(LED(pin) for pin in mux1_pins)

        # MUX2 controls S- and V- (A0, A1)
        self.mux2 = tuple(LED(pin) for pin in mux2_pins)

        # Turns MUXs off before switching and on again
        self.mux_toggle = tuple(LED(pin) for pin in mux_toggle)

        # Device manager
        self.dm = DeviceManager(scope_idn=scope_idn, wavegen_idn=wavegen_idn)

        # Classifier to return location of OHR
        self.classifier = Classifier()

        # Set to defaults to avoid classifier having no model
        self.set_object(object_name)
        self.set_model(model_name)

    # ========= Configure classifier =========

    def auto_calibration(self, object_name, n):
        """Run data collection script to make new model for new object, real-time."""
        new_obj_name = "auto_cal_" + object_name

        # n < 200 measurements per location, fast enough for real-time demo
        self.object_data(new_obj_name, n=n)

        self.set_object(new_obj_name)

    # For changing object and model for existing Classifier object, extra layer of abstraction
    def set_object(self, object_name):
        self.classifier.set_object(object_name)

    def set_model(self, model_name):
        self.classifier.set_model(model_name)

    def get_status(self):
        return f"object = {self.classifier.object_name}\nmodel = {self.classifier.model_name}"

    # ========= Get raw voltages and find location with classifier =========

    def get_voltages(self):
        """Get voltages from all 6 configurations with MUXs."""
        v_return = np.zeros(6)

        # (selection for MUX 1, selection for MUX 2, voltage measurement index)
        configs = [
            (2, 1, 1),  # V_AD
            (3, 2, 2),  # V_AB
            (1, 3, 3),  # V_BC
            (4, 4, 4),  # V_CD
            (2, 3, 5),  # V_AC: Diag
            (1, 1, 6),  # V_BD: Diag
        ]

        for s1, s2, index in configs:

            # Start MUX switch (ground measurement leads)
            self.mux_toggle[0].off()
            self.mux_toggle[1].off()

            # Switch MUX state
            self._set_mux_state(self.mux1, s1)  # Apply state to mux1
            self._set_mux_state(self.mux2, s2)  # Apply state to mux2

            # End MUX switch (turn measurement leads on)
            self.mux_toggle[0].on()
            self.mux_toggle[1].on()

            # Get voltage, assign to index
            # (V_AD, V_AB, V_BC, V_CD, V_AC, V_BD)
            v_return[index - 1] = self.dm.get_voltage()

        print(f"[SimpleEIT]: Measured voltages: {v_return}")

        return v_return

    def run(self, return_raw=False):
        """Get voltages, convert to probability distribution."""

        # Get the measured voltages
        # (V_AD, V_AB, V_BC, V_CD, V_AC, V_BD)
        v_raw = self.get_voltages()

        if return_raw is True:
            return v_raw
        else:
            # Use classifier

            # Matrix OHR locations:
            # [AB_1, AB_2, AD_1, AD_2, CD_1, CD_2, BC_1, BC_2]
            # [AB_3, AB_4, AD_3, AD_4, CD_3, CD_4, BC_3, BC_4]
            prediction = self.classifier.predict(v_raw)
            return prediction

    # ========= Context manager =========

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self.dm.close()

    # ========= Helper functions =========

    def _set_mux_state(self, mux, state):
        """Set MUX selection lines using GPIO."""
        # mux = (A0, A1)
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

    # ========= Helper functions =========

    @staticmethod
    def _write_header_if_empty(file_obj, writer, header):
        if file_obj.tell() == 0:
            writer.writerow(header)

    @staticmethod
    def _timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ========= EIT data collection scripts (hack because of circular import, TODO: fix) =========

    def object_data(self, object_name, n=10):
        print(f"[DataCollector]: Getting data for {object_name}...")

        if not object_name:
            raise RuntimeError("[DataCollector]: Object name cannot be empty!")

        csv_path = DATA_DIR / f"{object_name}_data.csv"

        header = [
            "Timestamp",
            "Location",
            "V_AB",
            "V_AD",
            "V_BC",
            "V_CD",
            "V_AC",
            "V_BD",
        ]

        locations = [
            f"{pair}_{i}" for pair in ("AB", "AD", "BC", "CD") for i in range(1, 5)
        ]

        with csv_path.open(mode="a", newline="") as f:
            writer = csv.writer(f)
            self._write_header_if_empty(f, writer, header)

            for location in locations:
                print(f"[DataCollector]: Move {object_name} to: {location}")
                input("[DataCollector]: Press enter when ready...")

                for i in range(n):
                    print(
                        f"[DataCollector]: Location: {location}, Measurement: {i + 1}/{n}"
                    )
                    values = self.run(return_raw=True)
                    writer.writerow([self._timestamp(), location, *values])

                print("[DataCollector]: Done, next location!")
