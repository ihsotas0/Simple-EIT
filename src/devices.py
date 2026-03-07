import pyvisa


class Devices:
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

    def set_voltmeter(self, command="CONF:VOLT:AC"):
        self.voltmeter.write(command)

    def set_wavegen(self, command="APPL:SIN 5E3,1,0.5"):
        self.wavegen.write(command)

    def get_voltage(self):
        return float(self.voltmeter.query("read?"))


class DeviceNotFoundError(Exception):
    """Raised when the requested device cannot be found."""

    pass
