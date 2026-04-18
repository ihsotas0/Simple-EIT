import csv
from datetime import datetime
from pathlib import Path

from simple_eit import SimpleEIT

# ========= Constants =========

DATA_DIR = Path("..") / "data"
FREQUENCIES = (1_000, 5_000, 10_000, 20_000)
INSTRUMENT_N = 1000
OBJECT_N = 200

# ========= Helper functions =========

def _write_header_if_empty(file_obj, writer, header):
    if file_obj.tell() == 0:
        writer.writerow(header)


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ========= EIT data collection scripts =========

def instrument_data():
    app = SimpleEIT()
    csv_path = DATA_DIR / "instrument_data.csv"

    header = [
        "Timestamp",
        "Frequency (Hz)",
        "V_AB",
        "V_AD",
        "V_BC",
        "V_CD",
        "V_AC",
        "V_BD",
    ]

    with csv_path.open(mode="a", newline="") as f:
        writer = csv.writer(f)
        _write_header_if_empty(f, writer, header)

        for freq in FREQUENCIES:
            for _ in range(INSTRUMENT_N):
                # Use DeviceManager to change frequency
                app.dm.change_frequency(freq)
                values = app.run(return_raw=True)
                writer.writerow([_timestamp(), freq, *values])


def object_data(object_name: str):
    if not object_name:
        raise RuntimeError("Object name cannot be empty!")

    app = SimpleEIT()
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
        _write_header_if_empty(f, writer, header)

        for location in locations:
            print(f"Move object to: {location}")
            input("Press enter when ready...")

            for i in range(OBJECT_N):
                print(f"[{location}] Measurement: {i + 1}/{OBJECT_N}")
                values = app.run(return_raw=True)
                writer.writerow([_timestamp(), location, *values])

            print("Done, next location!")

# ========= Main =========

def main():
    print("Running data collection script...")
    choice = input("Data to collect [Instrument: i, Object: o]: ").strip().upper()

    if choice == "I":
        instrument_data()
    elif choice == "O":
        object_name = input("Object name: ").strip()
        object_data(object_name)
    else:
        raise RuntimeError("Unknown input!")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
