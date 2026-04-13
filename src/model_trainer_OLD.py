import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from scipy.stats import mode

# -------------------------
# Load data
# -------------------------
df = pd.read_csv("../data/archive/vertical_eraser_no_salt_data_formatted.csv")
X = df.drop("Label", axis=1).values
y = df["Label"].values

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=1
)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -------------------------
# Helper for EM label alignment
# -------------------------
def align_labels(y_true, y_pred):
    aligned = np.zeros_like(y_pred)
    for i in np.unique(y_pred):
        mask = y_pred == i
        aligned[mask] = mode(y_true[mask], keepdims=True)[0]
    return aligned

# -------------------------
# Train and evaluate models
# -------------------------
results = {}
loss_histories = {}

# 1. MLP
mlp = MLPClassifier(hidden_layer_sizes=(10, 10), max_iter=10000, random_state=1, verbose=False)
mlp.fit(X_train, y_train)
results["MLP"] = accuracy_score(y_test, mlp.predict(X_test))
loss_histories["MLP"] = mlp.loss_curve_

# 2. Logistic Regression
log_reg = LogisticRegression(max_iter=2000)
log_reg.fit(X_train, y_train)
results["LogReg"] = accuracy_score(y_test, log_reg.predict(X_test))

# 3. KNN
knn = KNeighborsClassifier(n_neighbors=6)
knn.fit(X_train, y_train)
results["KNN"] = accuracy_score(y_test, knn.predict(X_test))

# 4. Linear (SGD)
sgd = SGDClassifier(max_iter=1000, tol=1e-3, random_state=1)
sgd.fit(X_train, y_train)
results["SGD"] = accuracy_score(y_test, sgd.predict(X_test))
# Note: SGDClassifier does not store loss per epoch, but you could track via `partial_fit` in a loop

# 5. SVM
svm = SVC(kernel="rbf", C=1.0, gamma="scale")
svm.fit(X_train, y_train)
results["SVM"] = accuracy_score(y_test, svm.predict(X_test))

# 6. Expectation-Maximization (GMM)
gmm = GaussianMixture(n_components=len(np.unique(y_train)), random_state=1)
gmm.fit(X_train)
y_pred_gmm = align_labels(y_test, gmm.predict(X_test))
results["GMM (EM)"] = accuracy_score(y_test, y_pred_gmm)

# 7. Random Forest
rf = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42)
rf.fit(X_train, y_train)
results["Random Forest"] = accuracy_score(y_test, rf.predict(X_test))

# -------------------------
# Print results
# -------------------------
print("\nModel Comparison Results:")
for model, acc in results.items():
    print(f"{model}: {acc:.3f}")

# -------------------------
# Plot loss curves for models that support it
# -------------------------
plt.figure(figsize=(8,5))
for model_name, loss_curve in loss_histories.items():
    plt.plot(loss_curve, label=model_name)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.title("Training Loss vs Epochs")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
