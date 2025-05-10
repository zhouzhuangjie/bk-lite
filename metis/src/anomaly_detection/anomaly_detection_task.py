from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Union, Optional, Any, Callable
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, precision_score, recall_score, f1_score
import os
import joblib
from loguru import logger


class AnomalyDetectionTask(ABC):
    """
    异常检测任务的抽象基类

    提供异常检测的通用框架，包括数据加载、预处理、特征工程、模型训练和评估。
    子类只需实现特定的训练逻辑、预测方法和模型持久化操作。

    属性:
        name (str): 模型名称，用于日志和模型存储
        data (pd.DataFrame): 加载的原始数据集
        train_data (tuple): 训练数据集，格式为 (特征X, 标签y)
        val_data (tuple): 验证数据集，格式为 (特征X, 标签y)
        test_data (tuple): 测试数据集，格式为 (特征X, 标签y)
        model (Any): 训练好的模型实例
        feature_columns (List[str]): 使用的特征列名称
    """

    def __init__(self, name: str = "base_anomaly_detector"):
        """
        初始化异常检测任务

        Args:
            name: 模型名称，用于模型存储和日志标识
        """
        self.name = name
        self.data = None
        self.train_data = None
        self.val_data = None
        self.test_data = None
        self.model = None
        self.feature_columns = None
        logger.info(f"初始化异常检测任务: {name}")

    # ==================== 数据加载与预处理 ====================

    def load_data(self, csv_files: List[str]) -> pd.DataFrame:
        """
        加载并合并CSV文件数据

        Args:
            csv_files: 包含时序数据的CSV文件路径列表

        Returns:
            合并后的DataFrame

        Raises:
            ValueError: 如果CSV文件缺少必要的列
        """
        logger.info(f"加载数据文件: {len(csv_files)}个")
        return self._load_data(csv_files)

    def _load_data(self, csv_files: List[str]) -> pd.DataFrame:
        """
        加载和合并包含'timestamp', 'value', 'label'列的CSV文件

        Args:
            csv_files: 数据文件路径列表

        Returns:
            合并后的DataFrame

        Raises:
            ValueError: 当文件缺少必要列时
        """
        frames = []
        for path in csv_files:
            df = pd.read_csv(path, parse_dates=['timestamp'])
            required_cols = {'timestamp', 'value', 'label'}
            if not required_cols.issubset(df.columns):
                raise ValueError(
                    f"CSV {path} must contain columns: {required_cols}")
            df = df.dropna(subset=['timestamp', 'value'])
            df = df[['timestamp', 'value', 'label']].sort_values('timestamp')
            frames.append(df)
        self.data = pd.concat(frames, ignore_index=True)
        logger.debug(f"数据加载完成，共{len(self.data)}行")
        return self.data

    def preprocess(self, freq: str = 'infer', window: int = 5) -> pd.DataFrame:
        """
        预处理数据，确保规律的时间间隔、填补缺失值并提取特征

        Args:
            freq: 时间序列频率，如'5min', '1H'等，'infer'表示自动推断频率
            window: 滑动窗口大小，用于特征提取

        Returns:
            预处理后的DataFrame

        Raises:
            RuntimeError: 当未先加载数据时
        """
        logger.info(f"预处理数据，时间间隔:{freq}，窗口大小:{window}")
        return self._preprocess(freq, window)

    def _preprocess(self, freq: str = 'infer', window: int = 5) -> pd.DataFrame:
        """
        确保时间序列具有规律间隔、填补缺失值并提取时序特征

        Args:
            freq: 时间序列频率
            window: 滑动窗口大小

        Returns:
            预处理后的DataFrame

        Raises:
            RuntimeError: 当未先加载数据时
        """
        if self.data is None:
            raise RuntimeError("请先使用load_data()加载数据")

        frames = []
        for date, group_df in self.data.groupby(self.data['timestamp'].dt.date):
            df = group_df.set_index('timestamp')

            # 处理频率推断
            if freq == 'infer':
                # 计算最常见的时间间隔作为频率
                time_diffs = df.index.to_series().diff().dropna()
                if not time_diffs.empty:
                    most_common_diff = time_diffs.value_counts().index[0]
                    inferred_freq = pd.tseries.frequencies.to_offset(
                        most_common_diff)
                    df = df.asfreq(inferred_freq)
                else:
                    # 如果无法推断，使用默认5分钟
                    df = df.asfreq('5min')
                    logger.warning(f"无法推断频率，使用默认值5min，日期: {date}")
            else:
                df = df.asfreq(freq)

            # 填充缺失值
            df['value'] = df['value'].interpolate(method='linear').fillna(
                method='bfill').fillna(method='ffill')
            df['label'] = df['label'].fillna(0)

            # 使用共享的特征提取逻辑
            df = self._extract_features(df, window)
            frames.append(df)

        self.data = pd.concat(frames, ignore_index=True).dropna()

        logger.info(
            f"预处理完成，特征数量: {len(self.feature_columns)}，数据点总数: {len(self.data)}")
        return self.data

    def _extract_features(self, df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """
        提取时序特征的核心逻辑，被_preprocess和process_external_data共享

        实现了多种时序特征的提取:
        - 统计特征: 均值、标准差、最小值、最大值、中位数
        - 差分特征: 一阶差分、二阶差分
        - Z分数: 当前值相对于滚动窗口的标准化得分
        - 趋势特征: 线性拟合斜率
        - 自相关: 滞后1期的自相关系数
        - 时间特征: 小时、分钟、星期几、月份、是否周末

        Args:
            df: 包含时间序列数据的DataFrame
            window: 滑动窗口大小

        Returns:
            添加了特征的DataFrame
        """
        # 确保df有时间戳索引
        if 'timestamp' not in df.index.names and 'timestamp' in df.columns:
            df = df.set_index('timestamp')

        # 保存原始值列副本
        value_column = df['value'].copy()

        # 统计特征
        df['rolling_mean'] = value_column.rolling(
            window=window, min_periods=1).mean()
        df['rolling_std'] = value_column.rolling(
            window=window, min_periods=1).std().fillna(1e-5)  # 避免除零错误
        df['rolling_min'] = value_column.rolling(
            window=window, min_periods=1).min()
        df['rolling_max'] = value_column.rolling(
            window=window, min_periods=1).max()
        df['rolling_median'] = value_column.rolling(
            window=window, min_periods=1).median()
        df['diff_1'] = value_column.diff().fillna(0)
        df['diff_2'] = df['diff_1'].diff().fillna(0)
        df['zscore'] = (value_column - df['rolling_mean']) / df['rolling_std']

        # 添加趋势特征
        df['trend'] = value_column.rolling(window=window, min_periods=1).apply(
            lambda x: np.polyfit(np.arange(len(x)), x, 1)[
                0] if len(x) > 1 else 0
        )

        # 季节性检测 - 自相关特征
        if len(value_column) >= window * 2:
            df['autocorr_1'] = value_column.rolling(window=window*2, min_periods=window).apply(
                lambda x: x.autocorr(lag=1) if len(x) > window else 0
            )
        else:
            df['autocorr_1'] = 0

        # 重置索引并添加时间特征
        df = df.reset_index()
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

        # 保存特征列名
        if self.feature_columns is None:
            self.feature_columns = [col for col in df.columns
                                    if col not in ['timestamp', 'label', 'index']]

        return df

    # ==================== 数据集划分 ====================

    def split_data(self, test_size: float = 0.2, val_size: float = 0.1,
                   random_state: int = 42) -> Tuple[Tuple[np.ndarray, np.ndarray],
                                                    Tuple[np.ndarray,
                                                          np.ndarray],
                                                    Tuple[np.ndarray, np.ndarray]]:
        """
        将数据分割为训练、验证和测试集

        Args:
            test_size: 测试集比例
            val_size: 验证集比例（相对于训练+验证集合）
            random_state: 随机种子，确保结果可复现

        Returns:
            (训练集, 验证集, 测试集)三元组，每个元素为(特征, 标签)对

        Raises:
            RuntimeError: 当未先预处理数据时
        """
        logger.info(f"拆分数据，测试集比例:{test_size}，验证集比例:{val_size}")
        return self._split_data(test_size, val_size, random_state)

    def _split_data(self, test_size: float = 0.2, val_size: float = 0.1,
                    random_state: int = 42) -> Tuple[Tuple[np.ndarray, np.ndarray],
                                                     Tuple[np.ndarray,
                                                           np.ndarray],
                                                     Tuple[np.ndarray, np.ndarray]]:
        """
        将数据分割为训练、验证和测试集，使用分层抽样确保各集合中异常比例一致

        Args:
            test_size: 测试集比例
            val_size: 验证集比例（相对于训练+验证集合）
            random_state: 随机种子，确保结果可复现

        Returns:
            (训练集, 验证集, 测试集)三元组，每个元素为(特征, 标签)对

        Raises:
            RuntimeError: 当未先预处理数据时
        """
        if self.data is None:
            raise RuntimeError("请先运行preprocess()预处理数据")

        feature_cols = self.feature_columns or [
            col for col in self.data.columns if col not in ['timestamp', 'label', 'index']]
        X = self.data[feature_cols].values
        y = self.data['label'].astype(int).values

        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, stratify=y, random_state=random_state
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=val_size, stratify=y_train_val, random_state=random_state
        )

        self.train_data = (X_train, y_train)
        self.val_data = (X_val, y_val)
        self.test_data = (X_test, y_test)

        logger.info(
            f"数据拆分完成: 训练集:{X_train.shape[0]}例, 验证集:{X_val.shape[0]}例, 测试集:{X_test.shape[0]}例")
        logger.debug(
            f"异常占比: 训练集:{np.mean(y_train):.4f}, 验证集:{np.mean(y_val):.4f}, 测试集:{np.mean(y_test):.4f}")
        return self.train_data, self.val_data, self.test_data

    # ==================== 外部数据处理 ====================

    def process_external_data(self, data: pd.DataFrame, freq: str = '5min', window: int = 5) -> np.ndarray:
        """
        处理外部数据，提取特征以便进行预测

        此方法允许将新的未见数据处理成与训练数据兼容的格式，以便进行异常检测。

        Args:
            data: 包含timestamp和value列的DataFrame
            freq: 时间序列频率
            window: 滑动窗口大小

        Returns:
            处理后的特征数组，可直接用于预测

        Raises:
            ValueError: 如果输入数据格式不正确
        """
        if 'timestamp' not in data.columns or 'value' not in data.columns:
            raise ValueError("输入数据必须包含'timestamp'和'value'列")

        # 确保timestamp是日期时间类型
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])

        # 设置时间索引并确保频率一致
        df = data.set_index('timestamp').asfreq(freq)

        # 填充可能的缺失值
        df['value'] = df['value'].interpolate(method='linear').fillna(
            method='bfill').fillna(method='ffill')

        # 使用共享的特征提取逻辑
        df = self._extract_features(df, window)

        # 处理NaN值
        df = df.fillna(0)

        # 提取特征列，确保与模型训练时的特征一致
        feature_cols = self.feature_columns or [col for col in df.columns
                                                if col not in ['timestamp', 'label', 'index']]

        # 检查是否所有需要的特征都存在
        missing_features = set(feature_cols) - set(df.columns)
        if missing_features:
            for feat in missing_features:
                logger.warning(f"特征 {feat} 缺失，将填充为0")
                df[feat] = 0

        logger.debug(f"外部数据处理完成，样本数: {len(df)}")
        # 返回特征数组
        return df[feature_cols].values

    # ==================== 模型评估 ====================

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        评估模型性能

        计算多种评估指标，包括精确率、召回率、F1分数和ROC AUC（如果适用）

        Args:
            y_true: 真实标签
            y_pred: 预测标签

        Returns:
            包含各项评估指标的字典
        """
        metrics = {
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0)
        }

        # 如果有足够的异常样本，计算AUC
        if len(set(y_true)) > 1:
            metrics["auc"] = roc_auc_score(y_true, y_pred)

        logger.debug(f"评估指标: {metrics}")
        return metrics

    # ==================== 模型持久化 ====================

    def save_model(self, model_path: str) -> None:
        """
        保存模型到指定路径

        将模型及其元数据（特征列，名称等）持久化到文件系统

        Args:
            model_path: 模型保存路径

        Raises:
            RuntimeError: 如果模型尚未训练
        """
        if self.model is None:
            raise RuntimeError("没有可保存的模型")

        # 确保目录存在
        os.makedirs(os.path.dirname(
            os.path.abspath(model_path)), exist_ok=True)

        logger.info(f"保存模型到: {model_path}")
        joblib.dump({
            "model": self.model,
            "feature_columns": self.feature_columns,
            "name": self.name
        }, model_path)
        logger.info(f"模型保存成功")

    def load_model(self, model_path: str) -> Any:
        """
        从指定路径加载模型

        加载模型及其元数据

        Args:
            model_path: 模型文件路径

        Returns:
            加载的模型数据

        Raises:
            FileNotFoundError: 当模型文件不存在时
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        logger.info(f"从{model_path}加载模型")
        model_data = joblib.load(model_path)
        self.feature_columns = model_data.get("feature_columns")
        self.name = model_data.get("name", self.name)
        logger.info(f"成功加载模型元数据: {self.name}")
        return model_data

    # ==================== 抽象方法（需子类实现） ====================

    @abstractmethod
    def train(self, train_config: Dict[str, Any] = None) -> Dict[str, float]:
        """
        训练模型的通用部分 - 数据准备逻辑

        子类应该调用此方法来处理通用的数据准备，然后实现特定的模型训练逻辑

        Args:
            train_config: 训练配置参数，可包含:
                - csv_files: 数据文件路径列表
                - freq: 时间序列频率
                - window: 滑动窗口大小
                - test_size: 测试集比例
                - val_size: 验证集比例
                - random_state: 随机种子
                - 以及特定模型的超参数

        Returns:
            包含训练评估指标的字典

        Raises:
            RuntimeError: 当数据未加载时
        """
        if train_config is None:
            train_config = {}

        # 数据处理
        self.load_data(train_config.get("csv_files", []))
        self.preprocess(
            freq=train_config.get("freq", "infer"),
            window=train_config.get("window", 5)
        )
        self.split_data(
            test_size=train_config.get("test_size", 0.2),
            val_size=train_config.get("val_size", 0.1),
            random_state=train_config.get("random_state", 42)
        )

        # 确保数据已加载
        if self.train_data is None:
            raise RuntimeError("训练数据未加载，请提供csv_files参数或先加载数据")

        # 返回空指标，子类应该填充并返回实际指标
        return {}

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        使用模型进行预测

        Args:
            X: 特征数据

        Returns:
            预测的异常标签 (1=异常, 0=正常)

        Raises:
            RuntimeError: 当模型未训练或加载时
        """
        pass
