import pyvisa

SCOPE_COMMAND_LIST = [
    "*RST",
    ":CHAN1:DISP ON",
    ":CHAN1:SCAL 1",  # 1 V/div
    ":TIM:SCAL 1E-4",  # 0.1 ms/div, reduce this to increase voltage measurement speed
    ":TRIG:EDGE:SOUR CHAN1",
    ":TRIG:EDGE:LEV 0",
    ":CHAN1:COUP AC",  # Removes DC offset from RMS calculation
]

# Models trained on these parameters
WAVEGEN_COMMAND_LIST = ["APPL:SIN 10e3,2.5,2.5"]

DEFAULT_TIMEOUT = 5000 # ms

class DeviceManager:
    """Encapsulates PyVISA for easy, error reporting instrument management."""

    def __init__(
        self,
        scope_idn,
        wavegen_idn,
        scope_commands=SCOPE_COMMAND_LIST,
        wavegen_commands=WAVEGEN_COMMAND_LIST,
        scope_timeout=DEFAULT_TIMEOUT,
        wavegen_timeout=DEFAULT_TIMEOUT,
    ):
        print("[DeviceManager]: Initializing devices...")

        self.rm = pyvisa.ResourceManager()
        self.wavegen = None
        self.scope = None

        # Filters out 'ASRL/dev/ttyS0::INSTR' serial issue
        resources = self.rm.list_resources("USB?*::INSTR")

        # Probe devices and check for error
        if self._probe_instruments(resources) is False:
            raise RuntimeError("[DeviceManager]: Can't probe devices!")

        # Select devices
        self.scope = self._find_by_idn(resources, scope_idn)
        self.wavegen = self._find_by_idn(resources, wavegen_idn)

        if self.scope is False or self.wavegen is False:
            raise RuntimeError(
                "[DeviceManager]: Could not identify required instruments!"
            )

        # Setup devices
        self.setup_device(self.scope, scope_timeout, scope_commands)
        self.setup_device(self.wavegen, wavegen_timeout, wavegen_commands)

        print("[DeviceManager]: Devices initialized successfully.")

    # ========= Context manager =========

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        """Close devices cleanly."""
        print("[DeviceManager]: Closing device connections...")
        self._close_resource(self.wavegen)
        self._close_resource(self.scope)
        self._close_resource(self.rm)
        print("Done!")

    # ========= Helper functions =========

    def _close_resource(self, resource):
        try:
            if resource:
                resource.close()
        except Exception as e:
            raise RuntimeError(f"[DeviceManager]: Error closing resource: {e}")

    def _probe_instruments(self, resources):
        print("[DeviceManager]: Probing instruments...")

        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                print("[DeviceManager]: Found instrument.")
                print(f"-> Resource: {resource}")
                print(f"-> IDN: {idn.strip()}")
                self._close_resource(inst)
            except Exception as e:
                print(f"[DeviceManager]: Probe failed for {resource}: {e}")
                return False

        return True

    def _find_by_idn(self, resources, keyword):
        """Select wavegen and scope by keyword."""
        print(f"[DeviceManager]: Selecting {keyword} instruments:")

        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                idn = inst.query("*IDN?")
                if keyword.upper() in idn.upper():
                    print(f"-> Selected resource: {resource}")
                    print(f"-> IDN: {idn.strip()}")
                    return inst
            except Exception as e:
                print(f"[DeviceManager]: Device selection failed for {resource}: {e}")
                return False

        # No devices returned, so return False to raise error in __init__
        return False

    # ========= Device setup and control =========

    def setup_device(self, device, timeout, command_list):
        """Use VISA commands to configure scope/wavegen."""
        try:
            device.timeout = timeout
            for command in command_list:
                device.write(command)

        except Exception as e:
            raise RuntimeError(f"[DeviceManager]: Failed to configure device: {e}")

    def change_frequency(self, freq):
        """For frequency testing of wavegen."""
        command = f"APPL:SIN {freq},2.5,2.5"
        try:
            self.wavegen.write(command)

        except Exception as e:
            raise RuntimeError(
                f"[DeviceManager]: Failed to change wavegen frequency: {e}"
            )

    def change_measurement_time(self, div):
        """Change time scale of scope to change single capture time."""
        command = f":TIM:SCAL {div}"
        try:
            self.scope.write(command)

        except Exception as e:
            raise RuntimeError(
                f"[DeviceManager]: Failed to change scope time scale: {e}"
            )

    # ========= Main output of DeviceManager =========

    def get_voltage(self):
        """Records scope RMS voltage over single capture."""
        try:

            # Trigger a fresh acquisition (fast single capture)
            self.scope.write(":DIG")

            # Wait until acquisition completes
            self.scope.query("*OPC?")

            # Query RMS voltage directly from scope
            rms_value = float(self.scope.query(":MEAS:VRMS? CHAN1"))
            return rms_value

        except Exception as e:
            raise RuntimeError(f"[DeviceManager]: Voltage read failed: {e}")


# ========= Testing =========

def basic_device_test():
    with DeviceManager() as dm:

        for i in range(25):
            voltage = dm.get_voltage()
            print(f"Test {i}: {voltage}")


if __name__ == "__main__":
    try:
        print("[DeviceManager]: Running basic device test...")
        basic_device_test()
    except RuntimeError as e:
        print(f"[DeviceManager]: Expected error: {e}")
    except Exception as e:
        print(f"[DeviceManager]: Unexpected error: {e}")
