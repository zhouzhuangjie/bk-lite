from typing import Any, Dict
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
from loguru import logger
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


class AnomalyDetectionTask:
    def __init__(self):
        self.data = None

        self.train_data = None
        self.val_data = None
        self.test_data = None

    def load_data(self, csv_file: str):
        logger.info(f"加载数据文件: {csv_file}")
        df = pd.read_csv(csv_file, parse_dates=['timestamp'])
        required_cols = {'timestamp', 'value', 'label'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV {csv_file} 必须包含列: {required_cols}")
        df = df.dropna(subset=['timestamp', 'value'])
        self.data = df[['timestamp', 'value', 'label']
        ].sort_values('timestamp')

    def _generate_features(self, df: pd.DataFrame, freq: str, window: int) -> (pd.DataFrame, list):
        df = df.set_index('timestamp')

        if freq == 'infer':
            time_diffs = df.index.to_series().diff().dropna()
            if not time_diffs.empty:
                inferred_freq = pd.tseries.frequencies.to_offset(
                    time_diffs.value_counts().index[0])
                logger.debug(f"推断频率: {inferred_freq}")
                df = df.asfreq(inferred_freq)
            else:
                df = df.asfreq('5min')
                logger.warning("无法推断频率，使用默认值5min")
        else:
            df = df.asfreq(freq)

        df['value'] = df['value'].interpolate(method='linear').fillna(
            method='bfill').fillna(method='ffill')
        df['label'] = df['label'].fillna(0)

        features = []
        df['rolling_mean'] = df['value'].rolling(window, min_periods=1).mean()
        features.append('rolling_mean')

        df['rolling_std'] = df['value'].rolling(
            window, min_periods=1).std().fillna(1e-5)
        features.append('rolling_std')

        df['rolling_min'] = df['value'].rolling(window, min_periods=1).min()
        features.append('rolling_min')

        df['rolling_max'] = df['value'].rolling(window, min_periods=1).max()
        features.append('rolling_max')

        df['rolling_median'] = df['value'].rolling(
            window, min_periods=1).median()
        features.append('rolling_median')

        df['diff_1'] = df['value'].diff().fillna(0)
        features.append('diff_1')

        df['diff_2'] = df['diff_1'].diff().fillna(0)
        features.append('diff_2')

        df['zscore'] = (df['value'] - df['rolling_mean']) / df['rolling_std']
        features.append('zscore')

        df['trend'] = df['value'].rolling(window, min_periods=1).apply(
            lambda x: np.polyfit(np.arange(len(x)), x, 1)[
                0] if len(x) > 1 else 0
        )
        features.append('trend')

        if len(df['value']) >= window * 2:
            df['autocorr_1'] = df['value'].rolling(window * 2, min_periods=window).apply(
                lambda x: x.autocorr(lag=1) if len(x) > window else 0
            )
        else:
            df['autocorr_1'] = 0
        features.append('autocorr_1')

        df = df.reset_index()
        df['hour'] = df['timestamp'].dt.hour
        features.append('hour')

        df['minute'] = df['timestamp'].dt.minute
        features.append('minute')

        df['dayofweek'] = df['timestamp'].dt.dayofweek
        features.append('dayofweek')

        df['month'] = df['timestamp'].dt.month
        features.append('month')

        df['is_weekend'] = df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
        features.append('is_weekend')

        df[features] = df[features].fillna(0)
        return df, features

    def preprocess(self, freq: str = 'infer', window: int = 5):
        self.data, self.feature_columns = self._generate_features(
            self.data, freq, window)
        logger.info(
            f"预处理完成，特征数量: {len(self.feature_columns)}，数据点总数: {len(self.data)}")

    def prepare_train_task(self, train_config: Dict[str, Any] = {}):
        self.train_config = train_config
        self.load_data(train_config['train_data_path'])

        freq = train_config.get('freq', 'infer')
        window = int(train_config.get('window', 5))
        self.preprocess(freq=freq, window=window)

        test_size = train_config.get('test_size', 0.2)
        val_size = train_config.get('val_size', 0.1)
        random_state = train_config.get('random_state', 42)

        X = self.data[self.feature_columns].values
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

        logger.debug(
            f"数据拆分完成: 训练集:{X_train.shape[0]}例, 验证集:{X_val.shape[0]}例, 测试集:{X_test.shape[0]}例")
        logger.debug(
            f"异常占比: 训练集:{np.mean(y_train):.4f}, 验证集:{np.mean(y_val):.4f}, 测试集:{np.mean(y_test):.4f}")

    def evaluate_model(self) -> dict:
        X_val, y_val = self.val_data
        y_pred = self.model.predict(X_val)

        return {
            "accuracy": accuracy_score(y_val, y_pred),
            "precision": precision_score(y_val, y_pred, zero_division=0),
            "recall": recall_score(y_val, y_pred, zero_division=0),
            "f1": f1_score(y_val, y_pred, zero_division=0),
        }

    def predict(self, input_df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"开始对{len(input_df)}条数据进行预测")

        required_cols = {'timestamp', 'value'}
        if not required_cols.issubset(input_df.columns):
            raise ValueError(f"输入数据必须包含列: {required_cols}")

        predict_df = input_df.copy()
        if 'label' not in predict_df.columns:
            predict_df['label'] = 0

        freq = self.train_config.get('freq', 'infer')
        window = int(self.train_config.get('window', 5))
        processed_df, features = self._generate_features(
            predict_df, freq, window)

        for col in self.feature_columns:
            if col not in processed_df.columns:
                processed_df[col] = 0

        X = processed_df[self.feature_columns].values
        y_pred = self.model.predict(X)

        result_df = input_df.copy()
        result_df['anomaly'] = y_pred

        logger.info(f"预测完成，检测到{sum(y_pred)}个异常点")
        return result_df

    def visualize_anomaly_detection_results(
            self,
            test_df: pd.DataFrame,
            y_pred: np.ndarray,
            title: str = "异常检测结果",
            output_path: str = "./test_results/anomaly_detection_result.png",
    ) -> dict:
        """
        可视化异常检测结果，对比预测结果和人工异常标注
        """
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS系统推荐字体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        window_offset = self.train_config.get("window_offset", 0)

        if "label" in test_df.columns:
            anomaly_indices = test_df.index[test_df["label"] == 1].to_numpy()
        else:
            anomaly_indices = np.array([])

        full_predictions = np.zeros(len(test_df), dtype=int)
        if len(y_pred) + window_offset <= len(full_predictions):
            full_predictions[window_offset:window_offset + len(y_pred)] = y_pred
        else:
            logger.warning("警告: 预测结果长度超过测试数据长度，结果将被截断！")
            valid_len = len(test_df) - window_offset
            full_predictions[window_offset:window_offset + valid_len] = y_pred[:valid_len]

        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 8))

        # 绘制时序数据和异常点
        ax.plot(test_df["timestamp"], test_df["value"], label="时序数据")

        predicted_anomalies = test_df[full_predictions == 1]
        ax.scatter(
            predicted_anomalies["timestamp"],
            predicted_anomalies["value"],
            color="red",
            marker="o",
            s=50,
            label="预测异常点",
        )

        if len(anomaly_indices) > 0:
            ax.scatter(
                test_df.iloc[anomaly_indices]["timestamp"],
                test_df.iloc[anomaly_indices]["value"],
                color="green",
                marker="x",
                s=80,
                label="实际异常点",
            )

        # 计算度量指标
        y_true = np.zeros(len(test_df), dtype=int)
        y_true[anomaly_indices] = 1
        valid_len = min(len(y_pred), len(test_df) - window_offset)
        metrics = {
            "accuracy": accuracy_score(y_true[window_offset:window_offset + valid_len], y_pred[:valid_len]),
            "precision": precision_score(
                y_true[window_offset:window_offset + valid_len],
                y_pred[:valid_len],
                zero_division=0
            ),
            "recall": recall_score(
                y_true[window_offset:window_offset + valid_len],
                y_pred[:valid_len],
                zero_division=0
            ),
            "f1": f1_score(
                y_true[window_offset:window_offset + valid_len],
                y_pred[:valid_len],
                zero_division=0
            ),
        }

        # 在图表中添加度量指标文本
        metrics_text = (
            f'准确率: {metrics["accuracy"]:.3f}(整体预测正确的比例)\n'
            f'精确率: {metrics["precision"]:.3f}(预测为异常中实际为异常的比例)\n'
            f'召回率: {metrics["recall"]:.3f}，(实际异常中被成功识别的比例)\n'
            f'F1分数: {metrics["f1"]:.3f}，(精确率与召回率的综合指标)'
        )

        plt.text(0.02, 0.98, metrics_text,
                 transform=ax.transAxes,
                 bbox=dict(facecolor='white', alpha=0.8),
                 verticalalignment='top',
                 fontsize=10)

        plt.title(title)
        plt.xlabel("时间")
        plt.ylabel("值")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"异常检测结果图保存到: {output_path}")
        logger.info(
            f"性能指标 - Precision: {metrics['precision']:.4f}, "
            f"Recall: {metrics['recall']:.4f}, "
            f"F1: {metrics['f1']:.4f}"
        )

        return metrics
