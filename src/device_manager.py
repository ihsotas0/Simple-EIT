import time
import numpy as np
import pyvisa


class ContinuousDeviceManager:
    """34470A digitize streaming for continuous RMS acquisition."""

    def __init__(self):
        print("Initializing devices...")
        self.rm = pyvisa.ResourceManager()
        self.voltmeter = None
        self.wavegen = None

        resources = self.rm.list_resources()
        if not resources:
            self.close()
            raise RuntimeError("No VISA resources found!")

        self._probe_instruments(resources)

        # Identify instruments by IDN
        self.voltmeter = self._find_by_idn(resources, "KEYSIGHT")
        self.wavegen = self._find_by_idn(resources, "AGILENT")

        if self.voltmeter is None or self.wavegen is None:
            self.close()
            raise RuntimeError("Could not find required instruments!")

        # Increase timeout for large transfers
        self.voltmeter.timeout = 20000
        self.wavegen.timeout = 5000

        print("Devices initialized successfully.")

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        print("Closing devices...")
        for r in [self.voltmeter, self.wavegen, self.rm]:
            try:
                if r:
                    r.close()
            except Exception as e:
                print(f"Error closing resource: {e}")
        print("Done!")

    # -------------------------
    # Helpers
    # -------------------------
    def _probe_instruments(self, resources):
        print("Found instruments:")
        for res in resources:
            try:
                inst = self.rm.open_resource(res)
                idn = inst.query("*IDN?")
                print(f"  {res}: {idn.strip()}")
                inst.close()
            except Exception as e:
                print(f"  {res} connection failed: {e}")

    def _find_by_idn(self, resources, keyword):
        for res in resources:
            try:
                inst = self.rm.open_resource(res)
                idn = inst.query("*IDN?")
                if keyword.upper() in idn.upper():
                    print(f"Selected {res}: {idn.strip()}")
                    return inst
                inst.close()
            except Exception as e:
                print(f"{res} connection failed: {e}")
        return None

    # -------------------------
    # Configure voltmeter once
    # -------------------------
    def configure_voltmeter(self, total_samples=100_000, voltage_range=10, aperture=20e-6):
        """Set up digitize mode for continuous streaming."""
        vm = self.voltmeter
        vm.write("*RST")
        vm.write("*CLS")

        vm.write("CONF:DIG:VOLT")  
        vm.write(f"DIG:VOLT:RANG {voltage_range}")
        vm.write(f"DIG:VOLT:APER {aperture}")
        vm.write(f"SAMP:COUN {total_samples}")  # large sample buffer
        vm.write("TRIG:SOUR IMM")
        vm.write("FORM:DATA REAL,32")

        # Start acquisition once
        vm.write("INIT")
        vm.query("*OPC?")  # wait for buffer ready
        print(f"Voltmeter configured for streaming, {total_samples} samples.")

    # -------------------------
    # Configure wave generator
    # -------------------------
    def configure_wavegen(self, freq=5e3, v_pp=2.5, offset=2.5):
        self.wavegen.write(f"APPL:SIN {freq},{v_pp},{offset}")
        print(f"Wavegen: {freq} Hz, {v_pp} Vpp, {offset} V offset")

    # -------------------------
    # Continuous RMS acquisition
    # -------------------------
    def stream_rms(self, chunk_size=5000):
        """
        Generator yielding RMS of successive chunks.
        chunk_size = number of samples per RMS calculation
        """
        vm = self.voltmeter
        while True:
            try:
                # Fetch next chunk from the ongoing buffer
                data = vm.query_binary_values("FETC?", datatype='f', container=np.array)
                if len(data) == 0:
                    # No more data; optionally re-trigger
                    vm.write("INIT")
                    vm.query("*OPC?")
                    continue

                # Split into chunks if larger than requested
                for start in range(0, len(data), chunk_size):
                    chunk = data[start:start+chunk_size]
                    rms = np.sqrt(np.mean(chunk**2))
                    yield rms

            except Exception as e:
                print(f"Streaming error: {e}")
                break