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
            # Optimized VISA code for faster measurements
            commands = [
                "*RST",
                "*CLS",
                "CONF:VOLT:AC 5",
                "SENS:VOLT:AC:BAND FAST",
                "VOLT:AC:ZERO:AUTO OFF",
                "SENS:VOLT:AC:RANG 5",
                "TRIG:SOUR IMM",
                "SAMP:COUN 1",
            ]
            for command in commands:
                self.voltmeter.write(command)

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
            self.voltmeter.write("READ?")
            response = self.voltmeter.read()

            # Get values from VISA response (for n samples)
            values = [float(x) for x in response.split(",")]

            # Return average of samples
            return sum(values) / len(values)

        except Exception as e:
            raise RuntimeError(f"Voltage read failed: {e}")


# Testing
def basic_device_test():
    with DeviceManager() as dm:
        dm.set_voltmeter()
        dm.set_wavegen()

        for i in range(10):
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
