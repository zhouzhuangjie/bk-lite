from typing import Optional, Dict, Any
from src.anomaly_detection.anomaly_detection_task import AnomalyDetectionTask
from src.anomaly_detection.xgbod_detector import XGBODDetector


class DetectorFactory:
    """
    异常检测器工厂类

    用于创建和获取不同类型的异常检测器，方便扩展新的检测算法
    """

    @staticmethod
    def get_detector(detector_type: str, params: Optional[Dict[str, Any]] = None) -> AnomalyDetectionTask:
        """
        获取指定类型的异常检测器

        Args:
            detector_type: 检测器类型名称
            params: 初始化参数

        Returns:
            实例化的异常检测器

        Raises:
            ValueError: 如果指定的检测器类型不存在
        """
        if params is None:
            params = {}

        name = params.get("name", f"{detector_type}_detector")

        if detector_type.lower() == "xgbod":
            return XGBODDetector(name=name)
        # 未来可以在这里添加更多类型的检测器
        # elif detector_type.lower() == "isolation_forest":
        #     return IsolationForestDetector(name=name)
        # elif detector_type.lower() == "lof":
        #     return LOFDetector(name=name)
        else:
            raise ValueError(f"未知的检测器类型: {detector_type}")
