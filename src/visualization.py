import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# # Load data
# df = pd.read_csv("../data/model_performance.csv")

# # Flip 'Radius' for x-axis
# x = 10 * df["Radius"][::-1].reset_index(drop=True).values

# # Prepare colors
# colors = plt.cm.tab10.colors
# num_models = len(df.drop(["Object", "Radius"], axis=1).columns)

# # Prepare figure
# fig, ax = plt.subplots(figsize=(6, 5))

# # Store mean y for later
# y_mean = (
#     df.drop(["Object", "Radius"], axis=1)
#     .iloc[::-1]
#     .reset_index(drop=True)
#     .mean(axis=1)
#     .values
# )

# # Plot each model, fit individually, compute R^2
# for i, col in enumerate(df.drop(["Object", "Radius"], axis=1).columns):
#     y = df[col][::-1].reset_index(drop=True).values
#     color = colors[i % len(colors)]

#     # Plot original points
#     ax.plot(0.8 + x - 0.2 * (i + 1), y, "o", color=color, label=f"{col}")

# x_fit = np.linspace(10*df["Radius"].min(), 10*df["Radius"].max(), 100)

# # Fit mean curve
# Y_lin_mean = np.log(1 - y_mean)
# mean_model = LinearRegression()
# mean_model.fit(x.reshape(-1, 1), Y_lin_mean)
# b_mean = -mean_model.coef_[0]
# m_mean = np.exp(mean_model.intercept_)
# y_fit_mean = 1 - m_mean * np.exp(-b_mean * x_fit)
# y_fit_mean_r_s = 1 - m_mean * np.exp(-b_mean * x)
# ax.plot(x, y_mean, "s", color="black", markersize=6, label="Mean")
# print(y_mean)
# print(y_fit_mean_r_s)
# r_s = r2_score(y_mean, y_fit_mean_r_s)
# ax.plot(
#     x_fit,
#     y_fit_mean,
#     "-",
#     color="black",
#     linewidth=2,
#     label=f"y = 1 - {m_mean:.2f} exp(-{b_mean:.2f} x)\nR^2 = {r_s:.2f}",
# )


# print(f"Trend: 1 - {m_mean:3f} exp(-{b_mean:3f} x)")

# # Set x-axis ticks to the exact radii

# # Proper ticks
# ax.set_xticks(x)
# ax.set_xticklabels([str(radius) for radius in x])

# # Make plot presentable
# ax.set_xlabel("OHR radius [mm]")
# ax.set_ylabel(f"Model accuracy on test data (n=3200 out of 16000)")
# ax.set_title(
#     f"Simple EIT Accuracy vs OHR Radius\n(values at same radius offset for readability)"
# )
# ax.grid(True, alpha=0.3)
# ax.legend(
#     ncol=2,
#     loc="lower right",
#     title=f"n=8 models",
#     #borderaxespad=4,
# )
# plt.tight_layout()
# plt.show()


df_a = pd.read_csv("../data/curc_a_data.csv")
df_b = pd.read_csv("../data/curc_b_data.csv")
df_c = pd.read_csv("../data/curc_c_data.csv")
df_d = pd.read_csv("../data/curc_d_data.csv")
df_e = pd.read_csv("../data/curc_e_data.csv")
df_i = pd.read_csv("../data/instrument_data.csv")
df_is = pd.read_csv("../data/instrument_salt_data.csv")

# Load your CSV
df = df_i

df = df.iloc[4000:]

# # Define voltages and frequencies
# voltages = ["V_AD", "V_AB", "V_BC", "V_CD", "V_AC", "V_BD"]
# frequencies = [1000, 5000, 10000, 20000]  # in Hz

# # Set up the figure: 6 rows (voltages) x 4 columns (frequencies)
# fig, axes = plt.subplots(nrows=6, ncols=4, figsize=(20, 18))
# fig.subplots_adjust(hspace=0.5, wspace=0.3)

# for i, voltage in enumerate(voltages):
#     for j, freq in enumerate(frequencies):
#         ax = axes[i, j]
#         # Select data for this voltage and frequency
#         data = df[df["Frequency (Hz)"] == freq][voltage]

#         # Plot histogram
#         counts, bins, patches = ax.hist(
#             data, bins=20, density=True, color="skyblue", edgecolor="black", alpha=0.7
#         )

#         # Fit normal distribution
#         mu, std = norm.fit(data)
#         x = np.linspace(bins[0], bins[-1], 100)
#         p = norm.pdf(x, mu, std)

#         # Overlay normal curve
#         ax.plot(x, p, "r", linewidth=2)

#         if i == 0:
#             ax.set_title(f"{freq/1000:.0f} kHz", fontsize=9)

#         if j == 0:
#             ax.set_ylabel(f"{voltage}", fontsize=9)

# plt.suptitle("Instrument Calibration and Verification Data", fontsize=20)
# plt.show()

# # Get unique frequencies and sort them
# frequencies = sorted(df['Frequency (Hz)'].unique())

# # List of voltage columns
# voltages = ['V_AD', 'V_AB', 'V_BC', 'V_CD', 'V_AC', 'V_BD']

# # Prepare figure with subplots for each voltage
# fig, axes = plt.subplots(2, 3, figsize=(18, 10))
# axes = axes.flatten()

# for i, voltage in enumerate(voltages):
#     data_per_freq = [df[df['Frequency (Hz)'] == f][voltage].values for f in frequencies]
    
#     axes[i].violinplot(data_per_freq, showmeans=True, showmedians=True)
#     axes[i].set_title(voltage)
#     axes[i].set_xticks([1, 2, 3, 4])
#     axes[i].set_xticklabels([f"{int(f/1000)} kHz" for f in frequencies])
#     axes[i].set_ylabel("Voltage (V)")

# plt.tight_layout()
# plt.show()

# Define colors for each frequency
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # blue, orange, green, red

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

frequencies = sorted(df['Frequency (Hz)'].unique())
voltages = ['V_AD', 'V_AB', 'V_BC', 'V_CD', 'V_AC', 'V_BD']

for i, voltage in enumerate(voltages):
    data_per_freq = []
    for f in frequencies:
        values = df[df['Frequency (Hz)'] == f][voltage].values
        lower, upper = np.percentile(values, [1, 99])
        clipped = np.clip(values, lower, upper)
        data_per_freq.append(clipped)
    
    vp = axes[i].violinplot(data_per_freq, showmeans=True, showmedians=True)
    
    # Color each violin
    for patch, color in zip(vp['bodies'], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor('black')
        patch.set_alpha(0.7)
    
    axes[i].set_title(voltage)
    axes[i].set_xticks([1, 2, 3, 4])
    axes[i].set_xticklabels([f"{int(f/1000)} kHz" for f in frequencies])
    axes[i].set_ylabel("Voltage (V)")

plt.tight_layout()
plt.show()