import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import pandas as pd

df = pd.read_csv("vertical_eraser_no_salt_data_formatted.csv")

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

voltages = ["V_AB", "V_AD", "V_BC", "V_CD", "V_AC", "V_BD"]

quadrants = ["AB", "AD", "BC", "CD"]

# # Initialize figure and axes
# fig, axes = plt.subplots(6, 16, figsize=(20, 50))

# # Loop through each subplot
# for col in range(16):

#     data = split_df[locations[col]]

#     for row in range(6):
#         ax = axes[row, col]

#         ax_data = data[voltages[row]]

#         # Fit a normal distribution to the data:
#         mu, std = norm.fit(ax_data)

#         # Plot the histogram.
#         ax.hist(ax_data, bins=10, density=True, alpha=0.6, color="g")

#         # Plot the PDF.
#         xmin, xmax = ax.get_xlim()
#         x = np.linspace(xmin, xmax, 100)
#         p = norm.pdf(x, mu, std)
#         ax.plot(x, p, "k", linewidth=2)

#         if col == 0:
#             ax.set_ylabel(voltages[row])

#         if row == 0:
#             ax.set_title(locations[col])

# # Adjust layout for better spacing
# #plt.tight_layout()
# plt.show()

# # Initialize figure and axes
# fig, axes = plt.subplots(6, 4, figsize=(20, 50))

# # Loop through each subplot
# for col in range(4):

#     # 0: 0:4
#     # 1: 4:8
#     # 2: 8:12
#     # 3: 12:16

#     col_data = df[
#         df["Label"].isin(locations[4*col:4*col+4])
#     ]

#     print(f"\n\n\nCOL: {col}: {col_data}\n\n\n")

#     for row in range(6):
#         ax = axes[row, col]

#         ax_data = col_data[voltages[row]]

#         # Fit a normal distribution to the data:
#         mu, std = norm.fit(ax_data)

#         # Plot the histogram.
#         ax.hist(ax_data, bins=10, density=True, alpha=0.6, color="g")

#         # Plot the PDF.
#         xmin, xmax = ax.get_xlim()
#         x = np.linspace(xmin, xmax, 100)
#         ax.set_xlim(0,1)
#         p = norm.pdf(x, mu, std)
#         ax.plot(x, p, "k", linewidth=2)

#         if col == 0:
#             ax.set_ylabel(voltages[row])

#         if row == 0:
#             ax.set_title(quadrants[col])

# # Adjust layout for better spacing
# # plt.tight_layout()
# plt.show()


# Initialize figure and axes
fig, axes = plt.subplots(6, 1, figsize=(20, 50))

colors = ["g", "r", "y", "b"]

# Loop through each subplot
for col in range(4):

    # 0: 0:4
    # 1: 4:8
    # 2: 8:12
    # 3: 12:16

    col_data = df[
        df["Label"].isin(locations[4*col:4*col+4])
    ]

    print(f"\n\n\nCOL: {col}: {col_data}\n\n\n")

    for row in range(6):
        ax = axes[row]

        ax_data = col_data[voltages[row]]

        # Fit a normal distribution to the data:
        mu, std = norm.fit(ax_data)

        # Plot the histogram.
        ax.hist(ax_data, bins=10, density=True, alpha=0.6, color=colors[col], label=quadrants[col])

        # Plot the PDF.
        xmin, xmax = ax.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        ax.plot(x, p, "k", linewidth=2, color=colors[col])

        if col == 0:
            ax.set_ylabel(voltages[row])

        if row == 0:
            ax.set_title(str(quadrants))
            ax.legend()

# Adjust layout for better spacing
# plt.tight_layout()
plt.show()
