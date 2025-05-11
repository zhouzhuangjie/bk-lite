from typing import Dict, Any

import joblib
from loguru import logger
from pyod.models.abod import ABOD
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.ocsvm import OCSVM
from pyod.models.knn import KNN
from pyod.models.suod import SUOD

from src.anomaly_detection.anomaly_detection_task import AnomalyDetectionTask


class SuodDetector(AnomalyDetectionTask):
    def __init__(self):
        super().__init__()

        self.feature_columns = []
        self.train_config = {}
        self.model = None

    def save_model(self, model_path: str):
        joblib.dump({
            'model': self.model,
            'feature_columns': self.feature_columns,
            'train_config': self.train_config,
        }, model_path)
        logger.info(f"模型保存到: {model_path}")

    def load_model(self, model_path: str):
        data = joblib.load(model_path)
        self.model = data['model']
        self.feature_columns = data['feature_columns']
        self.train_config = data['train_config']

    def train(self, train_config: Dict[str, Any] = {}):
        self.prepare_train_task(train_config)

        model_params = train_config['hyper_params']
        logger.info(f"开始训练XGBOD模型，参数: {model_params}")

        base_detectors = [
            LOF(n_neighbors=50),
            KNN(n_neighbors=50),
            ABOD(n_neighbors=50),
            IForest(n_estimators=100),
            OCSVM()
        ]

        self.model = SUOD(base_estimators=base_detectors, combination='average', verbose=True)

        X_train, y_train = self.train_data
        self.model.fit(X_train, y_train)
        logger.info("XGBOD模型训练完成")
