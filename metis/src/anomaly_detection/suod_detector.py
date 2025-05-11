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
