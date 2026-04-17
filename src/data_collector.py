import csv
import os
from datetime import datetime

import numpy as np

from simple_eit import SimpleEIT


# Takes about 30 minutes
def no_object_data():
    app = SimpleEIT()

    # Path to the CSV file (run script in this directory please!)
    csv_file_path = os.path.join("..", "data", "instrument_data.csv")

    # Open the CSV file in append mode
    with open(csv_file_path, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Check if the file is empty and write header if it's a new file
        if csvfile.tell() == 0:
            writer.writerow(
                [
                    "Timestamp",
                    "Frequency (Hz)",
                    "V_AB",
                    "V_AD",
                    "V_BC",
                    "V_CD",
                    "V_AC",
                    "V_BD",
                ]
            )

        # Test some different frequencies
        for freq in [1e3, 5e3, 10e3, 20e3]:
            # Run app 1000 times and append the result to the CSV file
            for _ in range(1000):
                v = app.run(testing=True, freq=freq)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp, int(freq)] + list(v))


# Takes about 30 minutes per object
def quadrant_object_data(object_name):
    app = SimpleEIT()

    # Replace "instrument" with the object_name in the file name
    csv_file_path = os.path.join("..", "data", f"{object_name}_data.csv")

    locations = [
        "AB_1",
        "AB_2",
        "AB_3",
        "AB_4",
        "AD_1",
        "AD_2",
        "AD_3",
        "AD_4",
        "BC_1",
        "BC_2",
        "BC_3",
        "BC_4",
        "CD_1",
        "CD_2",
        "CD_3",
        "CD_4",
    ]

    # Open the CSV file in append mode
    with open(csv_file_path, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Check if the file is empty and write header if it's a new file
        if csvfile.tell() == 0:
            writer.writerow(
                [
                    "Timestamp",
                    "Location",
                    "V_AB",
                    "V_AD",
                    "V_BC",
                    "V_CD",
                    "V_AC",
                    "V_BD",
                ]
            )

        for location in locations:
            print(f"Move object to: {location}")
            _ = input("Press enter when ready...")

            # Run app 200 times and append the result to the CSV file
            for i in range(200):

                print(f"Measurement: {i}/200")
                v = app.run(testing=True)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                writer.writerow([timestamp, location] + list(v))

            print("Done, next location")


if __name__ == "__main__":
    try:
        print("Running data collection script...")

        # Pick the right collection function
        choice = input("Data to collect (I: Instrument, Q: Quadrant): ")

        match choice:
            case "I":
                no_object_data()
            case "Q":
                object_name = input("Object name: ")
                if not object_name:
                    raise RuntimeError("Object name cannot be empty!")
                quadrant_object_data(object_name)
            case _:
                raise RuntimeError("Unknown input!")

    except RuntimeError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
