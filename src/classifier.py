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
TEST_SIZE = 0.2
CACHE_DIR = "../data/models/"

MODEL_FACTORY = {
    "gb": lambda: GradientBoostingClassifier(),
    "knn": lambda: KNeighborsClassifier(n_neighbors=6),
    "lda": lambda: LinearDiscriminantAnalysis(),
    "logreg": lambda: LogisticRegression(max_iter=2500),
    "mlp": lambda: MLPClassifier(
        hidden_layer_sizes=(10, 10), max_iter=2500, random_state=RANDOM_STATE
    ),
    "rf": lambda: RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "svm": lambda: SVC(kernel="rbf", probability=True),
    "xgb": lambda: XGBClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=4, verbosity=0
    ),
}


class Classifier:
    """
    Handles classifier models with dynamic switching and smart caching.
    CSV I/O and training are completely skipped if a valid cache exists.
    """

    def __init__(self, model_factory=MODEL_FACTORY, test_size=TEST_SIZE, cache_dir=CACHE_DIR):
        self.dataset_map = self._get_data_files()
        self.model_factory = model_factory

        self.object_name = None
        self.model_name = None
        self.test_size = test_size
        self._current_dataset_hash = None  # Cached hash to avoid repeated disk reads

        # Model and preprocessing state
        self.model = None
        self.scaler = None
        self.encoder = None
        self.data = {}

        # Metadata
        self.accuracy = None
        self.loss_curve = None
        self.training_timestamp = None

        self.cache_dir = cache_dir

        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    # ========= Public switching API =========

    def set_object(self, object_name, test_size=None):
        """Sets the target object/dataset. Clears state."""

        # Refresh dataset_map in case new data has been added
        self.dataset_map = self._get_data_files()

        if object_name not in self.dataset_map:
            raise RuntimeError(f"[Classifier]: Dataset '{object_name}' not recognized.")

        self.object_name = object_name
        if test_size is not None:
            self.test_size = test_size

        # Compute hash ONCE per object switch to avoid repeated CSV reads
        csv_path = self.dataset_map[self.object_name]
        self._current_dataset_hash = self._hash_file(csv_path)

        # Clear all state to prevent leakage
        self.data = {}
        self.model = None
        self.scaler = None
        self.encoder = None

        print(
            f"[Classifier]: Object set to '{object_name}'. CSV and training deferred until cache miss."
        )

        # Auto update currently selected model to new object if a model is selected, otherwise wait for model to be set
        if self.model_name is not None:
            self.set_model(self.model_name)

    def set_model(self, model_name):
        """Sets the target model. Checks cache first. Skips CSV and training on hit."""
        if not self.object_name:
            raise RuntimeError("[Classifier]: Call set_object() before set_model().")
        if model_name not in self.model_factory:
            raise KeyError(f"[Classifier]: Model '{model_name}' not supported.")

        self.model_name = model_name
        cache_path = self._get_cache_path()

        if cache_path.exists():
            self._load_from_cache(cache_path)
            print(
                f"[Classifier]: Cache hit. Loaded {self.model_name} for {self.object_name}. Load CSV and train skipped."
            )
        else:
            print(
                f"[Classifier]: Cache miss. Loading CSV for {self.object_name} and training {self.model_name}..."
            )
            self._prepare_data()
            self._train_and_cache(cache_path)

    # ========= Internal pipeline =========

    def _prepare_data(self, random_state=RANDOM_STATE):
        """Loads CSV, fits scaler/encoder, and splits data. Called only on cache miss."""
        df = pd.read_csv(self.dataset_map[self.object_name])

        # Fresh instances to guarantee clean state
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()

        x = df.drop(["Timestamp", "Label"], axis=1).values
        y = df["Label"].values

        y_encoded = self.encoder.fit_transform(y)
        x_scaled = self.scaler.fit_transform(x)

        x_train, x_test, y_train, y_test = train_test_split(
            x_scaled, y_encoded, test_size=self.test_size, random_state=random_state
        )

        self.data = {
            "x_train": x_train,
            "x_test": x_test,
            "y_train": y_train,
            "y_test": y_test,
        }

    def _train_and_cache(self, cache_path):
        """Instantiates, trains, evaluates, and saves to cache."""
        self.model = self.model_factory[self.model_name]()
        print(f"[Classifier]: Training {self.model_name}...")

        self.model.fit(self.data["x_train"], self.data["y_train"])

        self.loss_curve = getattr(self.model, "loss_curve_", "No curve")
        self.accuracy = self._evaluate()
        print(
            f"[Classifier]: Accuracy ({self.object_name} | {self.model_name}): {self.accuracy:.4f}"
        )

        self.training_timestamp = datetime.now().isoformat()
        self._save_cache(cache_path)

    def _evaluate(self):
        """Returns accuracy on test set."""
        if not self.data:
            raise RuntimeError("[Classifier]: Test data not available for evaluation.")
        preds = self.model.predict(self.data["x_test"])
        return accuracy_score(self.data["y_test"], preds)

    # ========= Cache I/O =========

    @staticmethod
    def _hash_file(filepath):
        """Fast, memory-efficient MD5 hash of a file."""
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _get_data_files():
        data_dir = Path("../data")
        result = {}

        for file in data_dir.glob("*_data.csv"):
            # Extract OBJECT_NAME from filename
            key = file.stem.replace("_data", "")
            result[key] = str(file)

        return result

    def _get_cache_path(self):
        """Builds cache filename using precomputed dataset hash."""
        return (
            Path(self.cache_dir)
            / f"{self.object_name}_{self.model_name}_{self._current_dataset_hash}.joblib"
        )

    def _load_from_cache(self, cache_path):
        """Restores model, scaler, encoder, and metadata. No CSV loaded."""
        print(f"[Classifier]: Loading cached model: {cache_path.name}")
        payload = joblib.load(cache_path)

        self.model = payload["model"]
        self.scaler = payload["scaler"]
        self.encoder = payload["encoder"]

        meta = payload["metadata"]
        self.accuracy = meta["accuracy"]
        self.loss_curve = meta["loss_curve"]
        self.training_timestamp = meta["timestamp"]

    def _save_cache(self, cache_path):
        """Serializes model, scaler, encoder, and metadata."""
        payload = {
            "model": self.model,
            "scaler": self.scaler,
            "encoder": self.encoder,
            "metadata": {
                "accuracy": self.accuracy,
                "loss_curve": self.loss_curve,
                "timestamp": self.training_timestamp,
            },
        }
        joblib.dump(payload, cache_path)
        print(f"[Classifier]: Cache saved at {cache_path}")

    # ========= Inference =========

    def predict(self, feature_vector):
        """Predicts and returns formatted probability matrix."""
        if self.model is None or self.scaler is None:
            raise RuntimeError(
                "[Classifier]: Model not loaded. Call set_model() first."
            )

        if feature_vector.shape != (6,):  # Expected: [V_AD, V_AB, V_BC, V_CD, V_AC, V_BD]
            raise ValueError(f"[Classifier]: Expected 6 voltage values, got {feature_vector.shape}")

        v = np.asarray(feature_vector).reshape(1, -1)
        v_scaled = self.scaler.transform(v)
        probs = self.model.predict_proba(v_scaled)[0]
        return self._format_as_matrix(probs)

    def _format_as_matrix(self, probs):
        """Maps probabilities to layout for Matplotlib circular display."""
        labels = self.encoder.classes_
        prob_map = dict(zip(labels, probs))

        grid_layout = [
            ["AB_1", "AB_2", "AD_1", "AD_2", "CD_1", "CD_2", "BC_1", "BC_2"],
            ["AB_3", "AB_4", "AD_3", "AD_4", "CD_3", "CD_4", "BC_3", "BC_4"],
        ]
        return np.array(
            [[prob_map.get(lbl, 0.0) for lbl in row] for row in grid_layout]
        )
