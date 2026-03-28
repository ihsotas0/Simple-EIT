import pyvisa

KEYSIGHT_VID = "10893"
AGILENT_VID = "2391"


class DeviceManager:
    """Encapsulates PyVISA for robust instrument management."""

    def __init__(self):
        print("Initializing devices...")

        self.rm = pyvisa.ResourceManager()
        self.wavegen = None
        self.voltmeter = None

        resources = self.rm.list_resources()

        # Select devices given VID
        keysight_resources = [r for r in resources if KEYSIGHT_VID in r]
        agilent_resources = [r for r in resources if AGILENT_VID in r]

        fail = False

        # Probe devices and check for error
        fail |= self._probe_instruments(keysight_resources, "Keysight")
        fail |= self._probe_instruments(agilent_resources, "Agilent")

        if not keysight_resources or not agilent_resources or fail:
            self.close()
            raise RuntimeError("Can't initialize devices!")

        # Select devices
        self.voltmeter = self._find_by_idn(keysight_resources, "KEYSIGHT")
        self.wavegen = self._find_by_idn(agilent_resources, "AGILENT")

        if self.voltmeter is None or self.wavegen is None:
            self.close()
            raise RuntimeError("Could not identify required instruments via IDN.")

        # Set timeouts (ms)
        # self.voltmeter.timeout = 5000
        # self.wavegen.timeout = 5000

        print("Devices initialized successfully.")

    # Context Manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # Close devices cleanly
    def close(self):
        print("Closing device connections...")
        try:
            if self.wavegen:
                self.wavegen.close()
        except Exception as e:
            print(f"Error closing wavegen: {e}")

        try:
            if self.voltmeter:
                self.voltmeter.close()
        except Exception as e:
            print(f"Error closing voltmeter: {e}")

        try:
            if self.rm:
                self.rm.close()
        except Exception as e:
            print(f"Error closing ResourceManager: {e}")

    # Helper functions
    def _probe_instruments(self, instruments, label):
        print(f"Found {label} instruments:")
        failed = False

        for resource in instruments:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                print(f"{resource} -> {idn.strip()}")
                inst.close()
            except Exception as e:
                print(f"{resource} -> Connection failed: {e}")
                failed = True

        return failed

    def _find_by_idn(self, resources, keyword):
        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                if keyword.upper() in idn.upper():
                    print(f"Selected {resource} ({idn.strip()})")
                    return inst
                inst.close()
            except Exception as e:
                print(f"Error identifying {resource}: {e}")
        return None

    # API
    def initialize_voltmeter(self):
        try:
            self.voltmeter.write("*RST")
            self.voltmeter.write("*CLS")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize voltmeter: {e}")

    def set_voltmeter(self, command="CONF:VOLT:AC", plc=0.02, samples=50):
        try:
            self.voltmeter.write(command)
            # Power line cycles are reduced to reduce measurement time
            self.voltmeter.write(f"VOLT:AC:NPLC {plc}")
            self.voltmeter.write("VOLT:AC:ZERO:AUTO OFF")
            # self.voltmeter.write(f"SAMP:COUN {samples}")
        except Exception as e:
            raise RuntimeError(f"Failed to configure voltmeter: {e}")

    # WARNING: Models trained on data with these parameters for wavegen!
    # Don't touch unless absolutely needed
    def set_wavegen(self, freq=1e3, v_pp=2.5, offset=2.5):
        try:
            command = f"APPL:SIN {freq},{v_pp},{offset}"
            self.wavegen.write(command)
        except Exception as e:
            raise RuntimeError(f"Failed to configure wave generator: {e}")

    def get_voltage(self):
        try:
            self.voltmeter.write("READ?")
            response = self.voltmeter.read()

            # Get values from VISA response (for n samples)
            values = [float(x) for x in response.split(",")]

            # Return average of samples
            return sum(values) / len(values)

        except Exception as e:
            raise RuntimeError(f"Voltage read failed: {e}")


# Testing
if __name__ == "__main__":
    try:
        with DeviceManager() as dm:
            dm.initialize_voltmeter()
            dm.set_voltmeter()
            dm.set_wavegen()

            for i in range(10):
                voltage = dm.get_voltage()
                print(f"{i}: {voltage:.6f}")

    except RuntimeError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
