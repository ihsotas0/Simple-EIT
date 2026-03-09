import pyvisa


class DeviceManager:
    """Encapsulates PyVISA for better usability."""

    def __init__(self):

        print("Initializing devices...")
        fail = 0

        # Get USB devices
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        # Find Keysight instruments (Vendor ID: 10893)
        keysight_instruments = [r for r in resources if "10893" in r]

        # Find Agilent instruments (Vendor ID: 2391)
        agilent_instruments = [r for r in resources if "2391" in r]

        # For debugging
        print("Found Keysight instruments:")
        for instrument in keysight_instruments:
            try:
                inst = rm.open_resource(instrument)
                idn = inst.query("*IDN?")
                print(f"  {instrument}\n  {idn.strip()}")
                inst.close()
            except:
                print(f"  {instrument}\n Connection failed")
                fail = 1

        print("Found Agilent instruments:")
        for instrument in agilent_instruments:
            try:
                inst = rm.open_resource(instrument)
                idn = inst.query("*IDN?")
                print(f"  {instrument}\n  {idn.strip()}")
                inst.close()
            except:
                print(f"  {instrument}\n Connection failed")
                fail = 1

        # Check if devices are not connected
        if fail == 1 or len(keysight_instruments) == 0 or len(agilent_instruments) == 0:
            raise DeviceNotFoundError("Can't initialize devices!")
        else:
            self.wavegen = rm.open_resource(agilent_instruments[0])
            self.voltmeter = rm.open_resource(keysight_instruments[0])
            print("Done.")

    def set_voltmeter(self, command="CONF:VOLT:AC", plc=0.02):
        # Basic setup
        self.voltmeter.write("*RST")
        self.voltmeter.write("*CLS")  # Clear error queue
        self.voltmeter.write(command)

        # Fast measurement optimizations
        self.voltmeter.write(f"VOLT:AC:NPLC {plc}") # Integration time in Power Line Cycles
        self.voltmeter.write("VOLT:AC:ZERO:AUTO OFF")  # Disable autozero for speed

    def set_wavegen(self, freq=5e3, v_pp=1, offset=0.5):
        command=f"APPL:SIN {freq},{v_pp},{offset}"
        self.wavegen.write(command)

    def get_voltage(self):
        return float(self.voltmeter.query("READ?"))


class DeviceNotFoundError(Exception):
    """Raised when the requested device cannot be found."""

    pass

if __name__ == "__main__":
    
    # For testing
    dm = DeviceManager()
    dm.set_voltmeter()
    dm.set_wavegen()
    for i in range(10):
        print(f"{i}: dm.get_voltage()")