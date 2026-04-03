import csv
import os
from datetime import datetime

import numpy as np

from simple_eit import SimpleEIT


# Testing
def no_object_data():
    # No classifier, just return the raw voltages
    app = SimpleEIT(lambda x: x)

    # Path to the CSV file (run script in this directory please!)
    csv_file_path = os.path.join("..", "data", "instrument_data.csv")

    # Open the CSV file in append mode
    with open(csv_file_path, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Check if the file is empty and write header if it's a new file
        if csvfile.tell() == 0:
            writer.writerow(["Timestamp", "Voltage_data"])

        # Run app 100 times and append the result to the CSV file
        for _ in range(100):
            v = app.run().flatten()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp] + list(v))


def quadrant_object_data(object_name):
    # "No classifier", just return the raw voltages
    app = SimpleEIT(lambda x: x)

    # Replace "instrument" with the object_name in the file name
    csv_file_path = os.path.join("..", "data", f"{object_name}_data.csv")

    previous_label = ""

    # Open the CSV file in append mode
    with open(csv_file_path, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Check if the file is empty and write header if it's a new file
        if csvfile.tell() == 0:
            writer.writerow(["Timestamp", "Voltage_data"])

        # Run app 100 times and append the result to the CSV file
        for _ in range(100):
            v = app.run().flatten()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prompt user for a label, defaulting to the previous label
            label = input(
                f"Enter a label for this data (previous label: {previous_label}): "
            )

            # If the user enters nothing, use previous label
            if not label:
                label = previous_label

            writer.writerow([timestamp] + list(v) + [label])
            previous_label = label


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
