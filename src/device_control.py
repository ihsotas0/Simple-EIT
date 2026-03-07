import pyvisa

def get_devices():

    # Connect and get instruments
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()

    # Find Keysight instruments (Vendor ID: 10893)
    keysight_instruments = [r for r in resources if "10893" in r]

    # Find Agilent instruments (Vendor ID: 2391)
    agilent_instruments = [r for r in resources if "2391" in r]

    # Keysight is our voltmeter, Agilent is our wavegen

    print("Found Keysight instruments:")
    for instrument in keysight_instruments:
        try:
            inst = rm.open_resource(instrument)
            idn = inst.query("*IDN?")
            print(f"  {instrument}: {idn.strip()}")
            inst.close()
        except:
            print(f"  {instrument}: Connection failed")

    print("Found Agilent instruments:")
    for instrument in agilent_instruments:
        try:
            inst = rm.open_resource(instrument)
            idn = inst.query("*IDN?")
            print(f"  {instrument}: {idn.strip()}")
            inst.close()
        except:
            print(f"  {instrument}: Connection failed")

if __name__ == "__main__":
    get_devices()


