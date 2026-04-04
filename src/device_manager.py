import time

import numpy as np
import pyvisa


class DeviceManager:
    """Encapsulates PyVISA for robust instrument management."""

    def __init__(self):
        print("Initializing devices...")

        self.rm = pyvisa.ResourceManager()
        self.wavegen = None
        self.voltmeter = None

        resources = self.rm.list_resources()

        fail = False

        # Probe devices and check for error
        fail |= self._probe_instruments(resources)

        if not resources or fail:
            self.close()
            raise RuntimeError("Can't initialize devices!")

        # Select devices
        self.voltmeter = self._find_by_idn(resources, "KEYSIGHT")
        self.wavegen = self._find_by_idn(resources, "AGILENT")

        if self.voltmeter is None or self.wavegen is None:
            self.close()
            raise RuntimeError("Could not identify required instruments via IDN!")

        # Set timeouts (ms)
        self.voltmeter.timeout = 5000
        self.wavegen.timeout = 5000

        print("Devices initialized successfully.")

    # Context Manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # Close devices cleanly
    def close(self):
        print("Closing device connections...")
        self._close_resource(self.wavegen)
        self._close_resource(self.voltmeter)
        self._close_resource(self.rm)
        print("Done!")

    # Helper functions
    def _close_resource(self, resource):
        try:
            if resource:
                resource.close()
        except Exception as e:
            print(f"Error closing resource: {e}")

    def _probe_instruments(self, instruments):
        print(f"Found instruments:")
        failed = False

        for resource in instruments:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                print(f"Found {resource}: {idn.strip()}")
                inst.close()
            except Exception as e:
                print(f"Connection failed {resource}: {e}")
                failed = True

        return failed

    def _find_by_idn(self, resources, keyword):
        print(f"Selecting {keyword} instruments:")
        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                if keyword.upper() in idn.upper():
                    print(f"Selected {resource}: {idn.strip()}")
                    return inst
                inst.close()
            except Exception as e:
                print(f"Connection failed {resource}: {e}")
        return None

    # API
    def set_voltmeter(self):
        try:
            self.voltmeter.write("*RST")
            self.voltmeter.write("*CLS")

            # -----------------------------
            # Configure fastest digitizing
            # -----------------------------

            # Digitize voltage mode
            self.voltmeter.write("CONF:DIG:VOLT")

            # Set range (IMPORTANT: avoid autorange for speed)
            self.voltmeter.write("DIG:VOLT:RANG 10")

            # Set fastest aperture (20 microseconds → 50 kSa/s)
            self.voltmeter.write("DIG:VOLT:APER 20E-6")

            # Number of samples
            num_samples = 5
            self.voltmeter.write(f"SAMP:COUN {num_samples}")

            # Trigger immediately
            self.voltmeter.write("TRIG:SOUR IMM")

            # Binary format (faster transfer)
            self.voltmeter.write("FORM:DATA REAL,32")
            self.voltmeter.write("INIT")

        except Exception as e:
            raise RuntimeError(f"Failed to configure voltmeter: {e}")

    # WARNING: Models trained on data with these default parameters for wavegen!
    # Don't touch unless absolutely needed
    def set_wavegen(self, freq=5e3, v_pp=2.5, offset=2.5):
        try:
            command = f"APPL:SIN {freq},{v_pp},{offset}"
            self.wavegen.write(command)
        except Exception as e:
            raise RuntimeError(f"Failed to configure wave generator: {e}")

    def get_voltage(self):
        try:

            self.voltmeter.write("ABOR")
            self.voltmeter.write("INIT")

            # Wait until acquisition finishes
            self.voltmeter.query("*OPC?")

            data = self.voltmeter.query_binary_values(
                "FETC?",
                datatype='f',
                container=np.array
            )

            rms = np.sqrt(np.mean(data**2))
            return rms

        except Exception as e:
            raise RuntimeError(f"Voltage read failed: {e}")


# Testing
def basic_device_test():
    with DeviceManager() as dm:
        dm.set_voltmeter()
        dm.set_wavegen()

        for i in range(25):
            voltage = dm.get_voltage()
            print(f"{i}: {voltage:.6f}")


if __name__ == "__main__":
    try:
        print("Running basic device test...")
        basic_device_test()
    except RuntimeError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
