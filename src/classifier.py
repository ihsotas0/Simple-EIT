import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

class Classifier:
    """
    Handles classifier models including caching, training, object and model
    selection, and output formatting.

    Input (v):
        [V_AD, V_AB, V_BC, V_CD, V_AC, V_BD]
    Output probability distribution: (sum=1)
        [[AB_1, AB_2, AD_1, AD_2, CD_1, CD_2, BC_1, BC_2],
         [AB_3, AB_4, AD_3, AD_4, CD_3, CD_4, BC_3, BC_4]]
    """

    def __init__(self, cache_dir: str = "../data/models/", random_state: int = 1):

        self.random_state = random_state

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Paths to collected CSV data
        self.dataset_map = {
            "vertical_eraser": "../data/archive/vertical_eraser_no_salt_data_formatted.csv",
        }

        # Model factory: uses lambdas to defer instantiation
        self.model_factory = {
            "gb": lambda: GradientBoostingClassifier(),
            "knn": lambda: KNeighborsClassifier(n_neighbors=6),
            "lda": lambda: LinearDiscriminantAnalysis(),
            "logreg": lambda: LogisticRegression(max_iter=2500),
            "mlp": lambda: MLPClassifier(
                hidden_layer_sizes=(10, 10),
                max_iter=2500,
                random_state=self.random_state,
            ),
            "rf": lambda: RandomForestClassifier(
                n_estimators=200, random_state=self.random_state
            ),
            "svm": lambda: SVC(kernel="rbf", probability=True),
            "xgb": lambda: XGBClassifier(
                n_estimators=300, learning_rate=0.05, max_depth=4, verbosity=0
            ),
        }

        # Internal state
        self.model_name = None
        self.object_name = None

        self.accuracy = None
        self.training_time = None
        self.loss_curve = None

        self.model = None
        self.dataset_hash = None

        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()

        self.data: Dict[str, np.ndarray] = {}

    # ========= UTILITIES =========

    def _hash_dataset(self, df: pd.DataFrame) -> str:
        """Creates a unique hash based on dataframe content."""
        return hashlib.md5(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()

    def _get_cache_path(self) -> Path:
        filename = f"{self.object_name}_{self.model_name}_{self.dataset_hash}.joblib"
        return self.cache_dir / filename

    # ========= LOAD OBJECT DATA =========

    def select_object(self, object_name: str, test_size: float = 0.2):
        """Loads, scales, and splits object voltage dataset."""
        if object_name not in self.dataset_map:
            raise KeyError(f"Dataset '{object_name}' not recognized.")

        # Get CSV and hash
        self.object_name = object_name
        df = pd.read_csv(self.dataset_map[object_name])
        self.dataset_hash = self._hash_dataset(df)

        # Get labels and voltages
        x = df.drop("Label", axis=1).values
        y = df["Label"].values

        # Preprocessing
        y_encoded = self.encoder.fit_transform(y)
        x_scaled = self.scaler.fit_transform(x)

        # Split dataset
        x_train, x_test, y_train, y_test = train_test_split(
            x_scaled, y_encoded, test_size=test_size, random_state=self.random_state
        )

        self.data = {
            "x_train": x_train,
            "x_test": x_test,
            "y_train": y_train,
            "y_test": y_test,
        }

    # ========= TRAIN MODEL AND CACHE =========

    def select_model(self, model_name: str):
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
        if not self.model or not self.data:
            raise RuntimeError("Must select object and model before training.")

        cache_path = self._get_cache_path()

        if cache_path.exists():
            print(f"Loading cached model: {cache_path.name}")
            payload = joblib.load(cache_path)
            self.model = payload["model"]
            self.accuracy = payload["metadata"]["accuracy"]
            self.training_time = payload["metadata"]["timestamp"]
            return

        print(f"Training {self.model_name}...")
        self.model.fit(self.data["X_train"], self.data["y_train"])

        if hasattr(self.model, "loss_curve_"):
            self.loss_curve = self.model.loss_curve_

        accuracy = self.evaluate()
        self._save_cache(cache_path, accuracy)

    def _save_cache(self, path: Path, accuracy: float):
        payload = {
            "model": self.model,
            "metadata": {"accuracy": accuracy, "timestamp": datetime.now().isoformat()},
        }
        joblib.dump(payload, path)
        print(f"Model saved at {path}. Accuracy: {accuracy:.4f}")

    # ========= Inference & Formatting =========

    def predict(self, feature_vector: list) -> np.ndarray:
        """Predicts and returns formatted 2x8 probability matrix."""
        v = np.array(feature_vector).reshape(1, -1)
        v_scaled = self.scaler.transform(v)

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(v_scaled)[0]
        else:
            # Fallback for models without predict_proba (e.g. basic Linear SVC)
            idx = self.model.predict(v_scaled)[0]
            probs = np.zeros(len(self.encoder.classes_))
            probs[idx] = 1.0

        return self._format_as_matrix(probs)

    def _format_as_matrix(self, probs: np.ndarray) -> np.ndarray:
        """Maps probabilities to a specific 2x8 sensor grid layout."""
        labels = self.encoder.classes_
        prob_map = dict(zip(labels, probs))

        # Define grid order based on experimental setup
        grid_layout = [
            ["AB_1", "AB_2", "AD_1", "AD_2", "CD_1", "CD_2", "BC_1", "BC_2"],
            ["AB_3", "AB_4", "AD_3", "AD_4", "CD_3", "CD_4", "BC_3", "BC_4"],
        ]

        try:
            return np.array(
                [[prob_map.get(lbl, 0.0) for lbl in row] for row in grid_layout]
            )
        except Exception as e:
            print(
                f"Warning: Formatting failed. Returning raw probabilities. Error: {e}"
            )
            return probs

    def evaluate(self) -> float:
        """Returns accuracy score on the test set."""
        preds = self.model.predict(self.data["X_test"])
        return accuracy_score(self.data["y_test"], preds)




