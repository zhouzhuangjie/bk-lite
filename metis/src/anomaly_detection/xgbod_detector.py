import joblib
from pyod.models.xgbod import XGBOD
from loguru import logger

from src.anomaly_detection.anomaly_detection_task import AnomalyDetectionTask


class XGBODDetector(AnomalyDetectionTask):
    """
    基于 XGBOD (XGBoost Outlier Detection) 的异常检测器

    使用 PyOD 库中的 XGBOD 实现，结合了无监督特征和 XGBoost 分类器
    """

    def __init__(self, name: str = "xgbod_detector"):
        """
        初始化 XGBOD 异常检测器

        Args:
            name: 模型名称，用于模型存储和日志
        """
        super().__init__(name=name)
        logger.info(f"初始化 XGBOD 异常检测器: {name}")

    def train(self, train_config: dict = None):
        """
        训练 XGBOD 模型

        Args:
            train_config: 配置字典，包含以下可选参数：
                - n_estimators: XGB树的数量，默认100
                - max_depth: 树的最大深度，默认3
                - learning_rate: 学习率，默认0.1
                - random_state: 随机种子，默认42
                - csv_files: CSV文件路径列表
                - freq: 时间序列频率，默认'infer'
                - window: 滑动窗口大小，默认5
                - test_size: 测试集占比，默认0.2
                - val_size: 验证集占比，默认0.1

        Returns:
            包含评估结果的字典
        """
        # 使用基类处理公共的数据准备逻辑
        super().train(train_config or {})

        # 模型特有的参数设置
        model_params = {
            "n_estimators": train_config.get("n_estimators", 100),
            "max_depth": train_config.get("max_depth", 3),
            "learning_rate": train_config.get("learning_rate", 0.1),
            "random_state": train_config.get("random_state", 42)
        }

        X_train, y_train = self.train_data

        logger.info(f"开始训练XGBOD模型，参数: {model_params}")
        self.model = XGBOD(**model_params)
        self.model.fit(X_train, y_train)
        logger.info("XGBOD模型训练完成")

        # 在验证集上评估
        X_val, y_val = self.val_data
        y_val_pred = self.predict(X_val)
        metrics = self.evaluate(y_val, y_val_pred)
        logger.info(f"验证集评估结果: {metrics}")

        return metrics

    def predict(self, X):
        """
        使用训练好的模型进行预测

        Args:
            X: 特征数组或DataFrame

        Returns:
            预测的异常标记 (1=异常, 0=正常)
        """
        if self.model is None:
            raise RuntimeError("模型尚未训练或加载")

        return self.model.predict(X)

    def load_model(self, model_path: str):
        """
        从指定路径加载模型

        Args:
            model_path: 模型文件路径
        """
        model_data = super().load_model(model_path)
        self.model = model_data.get("model")
        logger.info(f"成功加载XGBOD模型")
        return self.model
