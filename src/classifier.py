import hashlib
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

RANDOM_STATE = 1

# Paths to collected CSV data
DATASET_MAP = {
    "curc_a": "../data/curc_a_data.csv",
    "curc_b": "../data/curc_b_data.csv",
    "curc_c": "../data/curc_c_data.csv",
    "curc_d": "../data/curc_d_data.csv",
    "curc_e": "../data/curc_e_data.csv",
}

# Model factory: uses lambdas to defer instantiation
MODEL_FACTORY = {
    "gb": lambda: GradientBoostingClassifier(),
    "knn": lambda: KNeighborsClassifier(n_neighbors=6),
    "lda": lambda: LinearDiscriminantAnalysis(),
    "logreg": lambda: LogisticRegression(max_iter=2500),
    "mlp": lambda: MLPClassifier(
        hidden_layer_sizes=(10, 10),
        max_iter=2500,
        random_state=RANDOM_STATE,
    ),
    "rf": lambda: RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "svm": lambda: SVC(kernel="rbf", probability=True),
    "xgb": lambda: XGBClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=4, verbosity=0
    ),
}

CACHE_DIR = "../data/models/"

# Train / total
TEST_SIZE = 0.2


class Classifier:
    """
    Handles classifier models. Includes caching, training, object and model
    selection, and output formatting.

    Input (v):
        [V_AD, V_AB, V_BC, V_CD, V_AC, V_BD]
    Output probability distribution: (sum=1)
        [[AB_1, AB_2, AD_1, AD_2, CD_1, CD_2, BC_1, BC_2],
         [AB_3, AB_4, AD_3, AD_4, CD_3, CD_4, BC_3, BC_4]]
    """

    def __init__(self, object_name, model_name):

        print("[Classifier]: Initializing classifier...")

        # Make model cache directory if it doesn't exist
        cache_dir = Path(CACHE_DIR)
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.set_object(model_name)
        self.set_model(model_name)

        self.model = None

        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()

        self.data = {}

        print(f"[Classifier]: {model_name.upper()} for {object_name.upper()} initialized successfully.")

    # ========= UTILITIES =========

    def _get_cache_path(self, object_name, model_name, df):
        """Returns model cache file path for creation and retrival of file."""

        # Creates a unique hash based on dataframe content.
        dataset_hash = hashlib.md5(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()

        filename = f"{object_name}_{model_name}_{dataset_hash}.joblib"

        return Path(CACHE_DIR) / filename























    # ========= LOAD OBJECT DATA =========

    def set_object(self, object_name, test_size = TEST_SIZE):
        """Loads, scales, and splits object voltage dataset."""
        if object_name not in DATASET_MAP.keys():
            raise RuntimeError(f"[Classifier]: Dataset {object_name.upper()} not recognized.")

        # Get CSV
        df = pd.read_csv(self.dataset_map[object_name])

        cache_path = _get_cache_path(object_name)

        # Get labels and voltages
        x = df.drop(["Timestamp", "Label"], axis=1).values
        y = df["Label"].values

        # Preprocessing
        y_encoded = self.encoder.fit_transform(y)
        x_scaled = self.scaler.fit_transform(x)

        # Split dataset
        x_train, x_test, y_train, y_test = train_test_split(
            x_scaled, y_encoded, test_size=test_size, random_state=RANDOM_STATE
        )

        self.data = {
            "x_train": x_train,
            "x_test": x_test,
            "y_train": y_train,
            "y_test": y_test,
        }

    # ========= TRAIN MODEL AND CACHE =========

    def set_model(self, model_name: str):
        """Instantiates the chosen model."""
        if model_name not in self.model_factory:
            raise KeyError(f"Model '{model_name}' not supported.")

        # Pick model
        self.model_name = model_name
        self.model = self.model_factory[model_name]()

        # Train and save, or load model
        self._train_or_load()

    def _train_or_load(self):
        """Check for existing cache, otherwise train and save."""
        # if not self.model or not self.data:
        #    raise RuntimeError("Must select object and model before training.")

        cache_path = self._get_cache_path()

        if cache_path.exists():
            print(f"Loading cached model: {cache_path.name}")
            payload = joblib.load(cache_path)
            self.model = payload["model"]
            self.accuracy = payload["metadata"]["accuracy"]
            self.loss_curve = payload["metadata"]["loss_curve"]
            self.training_timestamp = payload["metadata"]["timestamp"]
            return

        print(f"Training {self.model_name}...")
        self.model.fit(self.data["x_train"], self.data["y_train"])

        if hasattr(self.model, "loss_curve_"):
            self.loss_curve = self.model.loss_curve_
        else:
            self.loss_curve = "No curve"

        self.accuracy = self._evaluate()
        print(
            f"Model accuracy ({self.object_name} : {self.model_name}): {self.accuracy}."
        )

        self.training_timestamp = datetime.now().isoformat()
        self._save_cache(cache_path)

    def _save_cache(self, path: Path):
        payload = {
            "model": self.model,
            "metadata": {
                "accuracy": self.accuracy,
                "loss_curve": self.loss_curve,
                "timestamp": self.training_timestamp,
            },
        }
        joblib.dump(payload, path)
        print(f"Model saved at {path}.")

    # ========= Inference & Formatting =========

    def predict(self, feature_vector: list) -> np.ndarray:
        """Predicts and returns formatted probability matrix."""
        v = np.array(feature_vector).reshape(1, -1)
        v_scaled = self.scaler.transform(v)

        probs = self.model.predict_proba(v_scaled)[0]

        return self._format_as_matrix(probs)

    def _format_as_matrix(self, probs: np.ndarray) -> np.ndarray:
        """Maps probabilities to layout for Matplotlib circular display code."""
        labels = self.encoder.classes_
        prob_map = dict(zip(labels, probs))

        # Define grid order based on experimental setup
        grid_layout = [
            ["AB_1", "AB_2", "AD_1", "AD_2", "CD_1", "CD_2", "BC_1", "BC_2"],
            ["AB_3", "AB_4", "AD_3", "AD_4", "CD_3", "CD_4", "BC_3", "BC_4"],
        ]

        return np.array(
            [[prob_map.get(lbl, 0.0) for lbl in row] for row in grid_layout]
        )

    def _evaluate(self) -> float:
        """Returns accuracy score on the test set."""
        preds = self.model.predict(self.data["x_test"])
        return accuracy_score(self.data["y_test"], preds)
