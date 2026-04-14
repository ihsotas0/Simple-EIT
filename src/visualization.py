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

# df_a = pd.read_csv("../data/curc_a_data.csv")
# df_b = pd.read_csv("../data/curc_b_data.csv")
# df_c = pd.read_csv("../data/curc_c_data.csv")
# df_d = pd.read_csv("../data/curc_d_data.csv")
# df_e = pd.read_csv("../data/curc_e_data.csv")
# df_i = pd.read_csv("../data/instrument_data.csv")
# df_is = pd.read_csv("../data/instrument_salt_data.csv")

# # Load your CSV
# df = df_is

# # For df_is, not df_i
# df = df[~((df['V_BC'] > 7.7) | (df['V_AD'] > 7.9) | (df['V_AC'] > 9.2))].copy()

# frequencies = sorted(df['Frequency (Hz)'].unique())
# voltages = ['V_AD', 'V_AB', 'V_BC', 'V_CD', 'V_AC', 'V_BD']
# fig, axes = plt.subplots(1, 6, figsize=(18, 4))
# axes = axes.flatten()

# for i, voltage in enumerate(voltages):
#     axes[i].set_title(voltage)
#     axes[i].set_xticks([1, 2, 3, 4])
#     axes[i].set_xticklabels([f"{int(f/1000)} kHz" for f in frequencies])
#     if i == 0 or i == 3:
#         axes[i].set_ylabel("Voltage (V)")

#     axes[i].grid(True, which='both', axis='both', alpha=0.3)
    
#     for j, f in enumerate(frequencies):
#         values = df[df['Frequency (Hz)'] == f][voltage].values
#         lower, upper = np.percentile(values, [1, 99])
#         clipped = np.clip(values, lower, upper)

#         unique_vals = np.unique(clipped)
        
#         if len(unique_vals) >= 10:
#             # Bare violin plot: no color, no mean/median
#             vp = axes[i].violinplot([clipped], positions=[j+1], showextrema=False, showmeans=True)
#             # Remove color: make transparent edges
#             for patch in vp['bodies']:
#                 patch.set_facecolor('none')
#                 patch.set_edgecolor('black')
#                 patch.set_alpha(1.0)

#             vp['cmeans'].set_color('black')
#         else:
#             # Few points → scatter with width proportional to counts
#             unique_vals, counts = np.unique(clipped, return_counts=True)
#             max_count = counts.max()
#             for val, count in zip(unique_vals, counts):
#                 width = 0.05 + 0.25 * (count / max_count)  # min width 0.05, max width 0.3
#                 x_jitter = np.random.uniform(-width, width, size=count) + (j+1)
#                 axes[i].scatter(x_jitter, [val]*count, alpha=0.7, color='k')

# plt.suptitle("Instrument Voltage Distributions for Different Configurations and Frequencies (14% Saline, n=1000 per Distribution)")
# plt.tight_layout()
# plt.show()

# # Load your CSV
# df = df_e

# #df = df[df['Label'].str.startswith('AB')].copy()

# labels = sorted(df['Label'].unique())
# voltages = ['V_AD', 'V_AB', 'V_BC', 'V_CD', 'V_AC', 'V_BD']
# fig, axes = plt.subplots(2, 3, figsize=(18, 8))
# axes = axes.flatten()

# for i, voltage in enumerate(voltages):
#     axes[i].set_title(voltage)
#     axes[i].set_xticks(np.linspace(1,len(labels)+1,len(labels)))
#     if i >= 3:
#         axes[i].set_xticklabels([f"{f}" for f in labels], rotation=45, ha='right')
#     else:
#         axes[i].set_xticklabels([])
#     if i == 0 or i == 3:
#         axes[i].set_ylabel("Voltage (V)")

#     axes[i].grid(True, which='both', axis='both', alpha=0.3)
    
#     for j, f in enumerate(labels):
#         values = df[df['Label'] == f][voltage].values
#         lower, upper = np.percentile(values, [1, 99])
#         clipped = np.clip(values, lower, upper)

#         unique_vals = np.unique(clipped)
        
#         if len(unique_vals) >= 10:
#             # Bare violin plot: no color, no mean/median
#             vp = axes[i].violinplot([clipped], positions=[j+1], showextrema=False, showmeans=True)
#             # Remove color: make transparent edges
#             for patch in vp['bodies']:
#                 patch.set_facecolor('none')
#                 patch.set_edgecolor('black')
#                 patch.set_alpha(1.0)

#             vp['cmeans'].set_color('black')
#         else:
#             # Few points → scatter with width proportional to counts
#             unique_vals, counts = np.unique(clipped, return_counts=True)
#             max_count = counts.max()
#             for val, count in zip(unique_vals, counts):
#                 width = 0.05 + 0.25 * (count / max_count)  # min width 0.05, max width 0.3
#                 x_jitter = np.random.uniform(-width, width, size=count) + (j+1)
#                 axes[i].scatter(x_jitter, [val]*count, alpha=0.7, color='k')

# plt.suptitle("Instrument Voltage Distributions for Different Configurations and Sectors (object=curc_e, n=200 per Distribution)")
# plt.tight_layout()
# plt.show()
