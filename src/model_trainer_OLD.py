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

"""
Good — this is exactly the right question to ask at this point. Your results already show a clear pattern:

> MLP is outperforming everything else → your dataset has **nonlinear feature interactions**, not simple linear separability.

Let’s break down **why**, using your actual feature structure.

---

# 🧠 1. What your features actually look like

You have:

```
V_AB, V_AD, V_BC, V_CD, V_AC, V_BD
```

This is a **pairwise relationship feature space**.

That usually implies:

* distances / similarities between entities (A, B, C, D)
* or interaction strengths between pairs
* strong dependency structure (not independent features)

So your model is NOT solving:

> “Which feature is big?”

It is solving:

> “Which *combination of relationships* defines the label?”

---

# ⚠️ 2. Why linear models fail (LogReg / SGD)

Linear models assume:

```
class = w1*V_AB + w2*V_AD + ... + bias
```

But your data likely behaves like:

* V_AB matters **only if V_AC is high**
* V_BD matters **only relative to V_CD**
* interactions matter more than raw values

So the true rule looks like:

```
IF (V_AB - V_AC) > threshold AND (V_BC * V_CD) < threshold → class A
```

👉 This is **nonlinear + interaction-heavy**

That’s why:

* LogReg ≈ 0.72 (limited linear view)
* SGD collapses (0.43)

---

# 🌳 3. Why tree models would help (even though you didn’t run them yet)

Tree models split like:

```
IF V_AB < 0.4:
    IF V_AD > 0.75:
        class = AB_1
```

They naturally capture:

* thresholds
* feature interactions
* nonlinear partitions

👉 This is why Random Forest / Gradient Boosting usually beat LogReg here.

---

# 🧠 4. Why MLP wins (your key result: 0.812)

Your MLP:

```python
MLPClassifier(hidden_layer_sizes=(10, 10))
```

This works because it learns:

### Layer 1:

* combines raw pairwise signals
* builds intermediate “interaction detectors”

### Layer 2:

* combines interactions of interactions

So it effectively learns:

```
(V_AB × V_AC) + (V_BD - V_CD) → nonlinear embedding → class
```

---

# 🔬 5. What MLP is probably learning in your dataset

Based on structure, it likely forms hidden features like:

### 🔹 Interaction features:

* V_AB / V_AC
* V_AD - V_CD
* V_BC × V_BD

### 🔹 Contrast patterns:

* “A-related edges stronger than C-related edges”
* “B is a hub vs D is weakly connected”

---

# 📉 6. Why SVM underperformed (important insight)

Your SVM (0.625) suggests:

* RBF kernel is **not well tuned**
* or feature interactions are **not smooth Gaussian-like boundaries**

SVM works best when:

* classes form smooth, blob-like boundaries in feature space

But your data likely has:

> rule-based / relational structure rather than geometric clusters

---

# 🧪 7. Why GMM (EM) is weak

GMM assumes:

> data = mixture of Gaussian clouds

But your features are:

* structured
* relational
* constrained (pairwise system)

So clusters are NOT Gaussian → EM struggles.

---

# 🧭 8. The real story of your dataset

Your results strongly indicate:

### ✔ Best model type:

* Neural networks (MLP)
* Tree ensembles (you haven’t tested yet)

### ❌ Weak models:

* Linear models
* Pure clustering (GMM)
* Untuned SVM

---

# 🚀 9. What I would do next (high impact)

If you want to push beyond 0.812:

## Step 1 — Add feature interactions explicitly

```python
df["AB_minus_AC"] = df["V_AB"] - df["V_AC"]
df["BD_minus_CD"] = df["V_BD"] - df["V_CD"]
df["AB_times_AC"] = df["V_AB"] * df["V_AC"]
```

## Step 2 — Train Random Forest / Extra Trees

## Step 3 — Tune MLP properly

* larger hidden layers: (50, 50)
* early stopping
* learning rate decay

## Step 4 — Try XGBoost (likely best performer)

---

# 🧠 Final insight (most important)

Your dataset is not:

> “feature → label”

It is:

> “relationship graph → label”

That is exactly why:

* linear models fail
* MLP works
* tree ensembles will likely work even better

---

If you want, I can next:

* map your features into a **graph model (GNN-style interpretation)**
* or design a **feature engineering step that usually pushes accuracy past 0.85–0.90**
* or identify which features are actually driving MLP decisions using SHAP values
"""


"""
Your results already tell a lot about your dataset:

* **MLP (0.812)** → best so far → likely nonlinear structure
* **LogReg / KNN (~0.72)** → decent baseline separability
* **SVM (0.625)** → struggling → likely wrong kernel or tuning
* **SGD (0.438)** → linear model not suitable
* **GMM (0.562)** → weak clustering structure (unsupervised mismatch)

So your data is probably:

> ✔ nonlinear
> ✔ moderately separable
> ✔ small-to-medium sized
> ✔ not well modeled by simple linear boundaries

---

# 🔥 Models I strongly recommend next

## 1. Random Forest (VERY important next step)

This is usually the **first model to try after MLP/SVM**.

```python id="rf_model"
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42
)

rf.fit(X_train, y_train)
print("Random Forest:", accuracy_score(y_test, rf.predict(X_test)))
```

### Why it will likely improve:

* Handles nonlinear interactions
* Works well on small datasets
* No scaling required (but OK if already scaled)
* Robust to noise

---

## 2. Gradient Boosting (often BEST on tabular data)

```python id="gb_model"
from sklearn.ensemble import GradientBoostingClassifier

gb = GradientBoostingClassifier(random_state=42)
gb.fit(X_train, y_train)

print("Gradient Boosting:", accuracy_score(y_test, gb.predict(X_test)))
```

### Why:

* Learns corrections iteratively
* Often beats MLP on small structured datasets

---

## 3. XGBoost (if you’re allowed external libs)

This is usually top-tier for tabular data.

```python id="xgb_model"
from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9
)

xgb.fit(X_train, y_train)
print("XGBoost:", accuracy_score(y_test, xgb.predict(X_test)))
```

### Why:

* Industry standard for structured data
* Usually beats everything except tuned neural nets

---

## 4. Extra-Trees (Random Forest alternative)

```python id="extra_trees"
from sklearn.ensemble import ExtraTreesClassifier

et = ExtraTreesClassifier(
    n_estimators=300,
    random_state=42
)

et.fit(X_train, y_train)
print("Extra Trees:", accuracy_score(y_test, et.predict(X_test)))
```

### Why:

* More randomness → often better generalization than RF

---

## 5. Quadratic Discriminant Analysis (QDA)

Very underrated for small datasets:

```python id="qda_model"
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

qda = QuadraticDiscriminantAnalysis()
qda.fit(X_train, y_train)

print("QDA:", accuracy_score(y_test, qda.predict(X_test)))
```

### Why:

* Models class covariance separately
* Great when classes form “elliptical blobs”

---

# ⚠ About your MLP warning

```
Maximum iterations reached and not converged
```

This means:

* Your neural net is under-trained

Fix:

```python id="mlp_fix"
MLPClassifier(
    hidden_layer_sizes=(50, 50),
    max_iter=3000,
    learning_rate_init=0.001,
    early_stopping=True
)
```

---

# 🧠 What your results suggest

Given:

* MLP best
* Tree methods not tested yet
* Linear models weak

👉 You are in the classic regime:

> “structured nonlinear tabular classification problem”

This almost always means:

* Tree ensembles (RandomForest / XGBoost / ExtraTrees) will dominate
* MLP is your second-best baseline

---

# 🏆 What I would try next (priority order)

1. **RandomForestClassifier**
2. **ExtraTreesClassifier**
3. **GradientBoostingClassifier**
4. **XGBoost (if allowed)**
5. Tune MLP properly
6. Try feature engineering (ratios between V_AB, V_AC, etc.)

---

If you want, I can next:

* Build a **single AutoML-style benchmark script**
* Or help you get from **0.81 → ~0.90+ (likely possible here)**
* Or analyze your features to see *why MLP wins* and what structure it’s learning
"""
