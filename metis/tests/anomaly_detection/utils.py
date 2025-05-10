import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def visualize_anomaly_detection_results(test_df, y_pred, anomaly_indices, window_offset, detector,
                                        title="异常检测结果",
                                        output_path="./test_results/anomaly_detection_result.png"):
    """
    通用的异常检测结果可视化和评估函数

    参数:
        test_df: 测试数据DataFrame，包含timestamp和value列
        y_pred: 预测结果数组
        anomaly_indices: 人工标记的异常点索引
        window_offset: 窗口偏移量
        detector: 检测器对象，用于调用evaluate方法
        title: 图表标题
        output_path: 输出图片路径

    返回:
        评估指标字典
    """
    # 将预测结果扩展到与测试数据相同的长度
    full_predictions = np.zeros(len(test_df), dtype=int)

    # 检查长度是否匹配预期，并调整偏移量
    expected_pred_len = len(test_df) - window_offset

    # 如果预测长度与期望不符，调整窗口偏移
    if len(y_pred) != expected_pred_len:
        print(f"警告: 预测长度({len(y_pred)})与期望长度({expected_pred_len})不符")
        window_offset = len(test_df) - len(y_pred)
        print(f"调整窗口偏移量为: {window_offset}")

    # 确保索引在有效范围内
    if window_offset >= 0 and len(y_pred) + window_offset <= len(full_predictions):
        full_predictions[window_offset:window_offset + len(y_pred)] = y_pred
    else:
        # 如果索引范围超出，可能需要截断预测结果
        valid_length = min(len(full_predictions) - window_offset, len(y_pred))
        full_predictions[window_offset:window_offset +
                                       valid_length] = y_pred[:valid_length]
        print(f"警告: 预测结果长度调整为 {valid_length}")

    # 可视化结果
    plt.figure(figsize=(14, 6))
    plt.plot(test_df['timestamp'], test_df['value'], label='时序数据')

    # 标记预测的异常点（使用红色）
    anomaly_points = test_df[full_predictions == 1]
    plt.scatter(anomaly_points['timestamp'], anomaly_points['value'],
                color='red', marker='o', s=50, label='预测异常点')

    # 标记人为设定的异常点位置（使用绿色）
    plt.scatter(test_df.iloc[anomaly_indices]['timestamp'],
                test_df.iloc[anomaly_indices]['value'],
                color='green', marker='x', s=80, label='实际异常点')

    plt.title(title)
    plt.xlabel('时间')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 保存图片
    plt.savefig(output_path)
    print(f"异常检测结果图像已保存到: {output_path}")

    # 计算人为设置的异常点检出率
    anomaly_detected = sum(
        full_predictions[idx] for idx in anomaly_indices if idx >= window_offset)
    valid_anomalies = sum(1 for idx in anomaly_indices if idx >= window_offset)
    detection_rate = anomaly_detected / valid_anomalies if valid_anomalies > 0 else 0
    print(
        f"人为设置的异常点检出率: {anomaly_detected}/{valid_anomalies} = {detection_rate:.2%}")

    # 计算针对手动标记异常点的F1分数
    # 创建真实标签数组(ground truth)，只有手动设置的异常点为1
    y_true = np.zeros(len(test_df), dtype=int)
    y_true[anomaly_indices] = 1

    # 确保评估时长度匹配
    if len(y_pred) <= len(y_true) - window_offset:
        metrics = detector.evaluate(
            y_true[window_offset:window_offset + len(y_pred)], y_pred)
    else:
        # 如果预测结果比预期长，需要截断
        metrics = detector.evaluate(
            y_true[window_offset:], y_pred[:len(y_true) - window_offset])

    print(
        f"异常检测性能指标 - 精确率: {metrics['precision']:.4f}, 召回率: {metrics['recall']:.4f}, F1分数: {metrics['f1']:.4f}")

    return metrics


def generate_training_data(num_points=None):
    """
    生成训练数据，包含各种类型的异常
    """
    if num_points is None:
        num_points = 1 * 24 * 60

    timestamps = [datetime(2024, 1, 1) + timedelta(minutes=i)
                  for i in range(num_points)]

    # 正常值：非对称周期波动 + 噪声
    base = 30
    period1 = 24 * 60  # 24小时周期，以分钟为单位
    period2 = 60  # 1小时周期，以分钟为单位
    cycle = 10 * np.sin(2 * np.pi * np.arange(num_points) / period1) + \
            5 * np.sin(2 * np.pi * np.arange(num_points) / period2)
    noise = np.random.normal(0, 5, size=num_points)
    values = base + cycle + noise
    values = np.clip(values, 0, 100)

    labels = np.zeros(num_points, dtype=int)

    # 1. 暴涨异常
    spike_indices = np.random.choice(num_points, size=30, replace=False)
    values[spike_indices] = np.random.uniform(85, 100, size=30)
    labels[spike_indices] = 1

    # 2. 暴跌异常
    drop_indices = np.random.choice(
        list(set(range(num_points)) - set(spike_indices)), size=20, replace=False)
    values[drop_indices] = np.random.uniform(0, 5, size=20)
    labels[drop_indices] = 1

    # 3. 高频抖动异常
    jitter_start = np.random.choice(list(set(range(100, num_points - 20)) - set(spike_indices) - set(drop_indices)),
                                    size=10, replace=False)
    for start in jitter_start:
        jitter_vals = base + np.random.choice([10, 90], size=10)
        values[start:start + 10] = jitter_vals
        labels[start:start + 10] = 1

    # 4. 缓慢上升异常
    rise_start = np.random.choice(list(set(range(100, num_points - 30)) - set(spike_indices) - set(drop_indices)),
                                  size=8, replace=False)
    for start in rise_start:
        values[start:start + 15] = np.linspace(40, 90, 15)
        labels[start:start + 15] = 1

    return pd.DataFrame({
        "timestamp": timestamps,
        "value": values,
        "label": labels
    })


def generate_test_data(num_points=None):
    """
    生成测试数据，包含手动设置的异常点
    """
    if num_points is None:
        num_points = 1 * 24 * 60
    timestamps = [datetime(2024, 2, 1) + timedelta(minutes=i)
                  for i in range(num_points)]

    # 正常值：周期波动 + 噪声
    base = 35  # 基础值与训练数据稍有不同
    period1 = 24 * 60  # 24小时周期，以分钟为单位
    period2 = 60  # 1小时周期，以分钟为单位
    cycle = 12 * np.sin(2 * np.pi * np.arange(num_points) / period1) + \
            6 * np.sin(2 * np.pi * np.arange(num_points) / period2)
    noise = np.random.normal(0, 4, size=num_points)
    values = base + cycle + noise
    values = np.clip(values, 0, 100)

    # 人为制造异常点，均匀分布在时间序列中
    num_anomalies = 50
    anomaly_indices = np.linspace(
        100, num_points - 100, num_anomalies, dtype=int)

    for idx in anomaly_indices:
        if idx % 3 == 0:
            values[idx] = 90  # 暴涨
        elif idx % 3 == 1:
            values[idx] = 5  # 暴跌
        else:
            # 制造连续异常
            duration = np.random.randint(5, 15)
            end = min(idx + duration, num_points)
            if np.random.random() > 0.5:
                # 持续高值
                values[idx:end] = np.random.uniform(80, 95, end - idx)
            else:
                # 持续低值
                values[idx:end] = np.random.uniform(0, 8, end - idx)

            # 更新异常索引，加入连续异常的所有点
            additional_indices = list(range(idx + 1, end))
            anomaly_indices = np.append(anomaly_indices, additional_indices)

    # 确保异常索引唯一且排序
    anomaly_indices = sorted(list(set(anomaly_indices)))

    return pd.DataFrame({
        "timestamp": timestamps,
        "value": values
    }), anomaly_indices


def generate_cpu_usage_data(num_points=1000, anomaly_percentage=0.05):
    """
    生成模拟CPU使用率的数据，包含多种真实场景的异常

    Args:
        num_points: 数据点数量
        anomaly_percentage: 异常点占总数据的百分比

    Returns:
        包含时间戳、CPU使用率值和标签的DataFrame，以及异常点索引列表
    """
    timestamps = [datetime(2024, 1, 1) + timedelta(minutes=5 * i)
                  for i in range(num_points)]

    # 基础负载模式
    # 工作日模式：工作时间(9:00-18:00)负载较高，其他时间较低
    # 周末负载整体较低
    base_load = np.zeros(num_points)
    for i in range(num_points):
        dt = timestamps[i]
        hour = dt.hour
        is_weekend = dt.weekday() >= 5

        if is_weekend:
            # 周末基础负载
            base_load[i] = 20
        else:
            # 工作日
            if 9 <= hour < 18:
                # 工作时间
                base_load[i] = 45
            else:
                # 非工作时间
                base_load[i] = 25

    # 添加日常波动
    daily_pattern = 10 * \
                    np.sin(2 * np.pi * np.arange(num_points) / (24 * 12))  # 24小时周期
    hourly_pattern = 5 * \
                     np.sin(2 * np.pi * np.arange(num_points) / 12)  # 1小时周期

    # 随机噪声
    noise = np.random.normal(0, 3, size=num_points)

    # 组合所有模式
    values = base_load + daily_pattern + hourly_pattern + noise
    values = np.clip(values, 0, 100)

    # 生成标签
    labels = np.zeros(num_points, dtype=int)

    # 确定异常点数量
    num_anomalies = int(num_points * anomaly_percentage)
    anomaly_indices = []

    # 1. CPU突发高负载（例如批处理任务）
    high_load_starts = np.random.choice(
        range(num_points - 10), size=num_anomalies // 5, replace=False)
    for start in high_load_starts:
        duration = np.random.randint(3, 8)
        end = min(start + duration, num_points)
        # 逐渐上升然后下降的峰值
        peak = np.random.uniform(85, 95)

        # 生成峰值形状
        peak_pattern = np.concatenate([
            np.linspace(values[start], peak, duration // 2 + 1),
            np.linspace(
                peak, values[min(end, num_points - 1)], duration - duration // 2)
        ])

        values[start:end] = peak_pattern[:end - start]
        labels[start:end] = 1
        anomaly_indices.extend(range(start, end))

    # 2. 内存泄漏模拟 - CPU使用率缓慢而持续地增长
    leak_starts = np.random.choice(
        range(num_points // 2), size=num_anomalies // 10, replace=False)
    for start in leak_starts:
        duration = np.random.randint(20, 40)
        end = min(start + duration, num_points)
        # 计算斜率，使CPU负载持续增加
        current = values[start]
        target = min(current + np.random.uniform(20, 40), 100)

        slope = (target - current) / duration
        for i in range(start, end):
            values[i] = current + slope * (i - start) + np.random.normal(0, 1)

        values[start:end] = np.clip(values[start:end], 0, 100)
        labels[start:end] = 1
        anomaly_indices.extend(range(start, end))

    # 3. 服务崩溃 - CPU使用率突然下降到接近零
    crash_indices = np.random.choice(
        list(set(range(num_points)) - set(anomaly_indices)),
        size=num_anomalies // 10,
        replace=False
    )
    for idx in crash_indices:
        duration = np.random.randint(3, 8)
        end = min(idx + duration, num_points)
        values[idx:end] = np.random.uniform(0, 5, size=end - idx)
        labels[idx:end] = 1
        anomaly_indices.extend(range(idx, end))

    # 4. 单点异常 - 短暂的CPU飙升
    spike_indices = np.random.choice(
        list(set(range(num_points)) - set(anomaly_indices)),
        size=num_anomalies // 3,
        replace=False
    )
    values[spike_indices] = np.random.uniform(85, 100, size=len(spike_indices))
    labels[spike_indices] = 1
    anomaly_indices.extend(spike_indices)

    # 确保异常索引唯一且排序
    anomaly_indices = sorted(list(set(anomaly_indices)))

    return pd.DataFrame({
        "timestamp": timestamps,
        "value": values,
        "label": labels
    }), anomaly_indices


def generate_complex_operational_data(metric_type="cpu", num_points=1000, anomaly_percentage=0.05):
    """
    生成复杂的运维场景数据，包括多种指标类型

    Args:
        metric_type: 指标类型，可选 "cpu", "memory", "network", "disk_io"
        num_points: 数据点数量
        anomaly_percentage: 异常点占比

    Returns:
        包含时间戳、指标值和标签的DataFrame，以及异常点索引列表
    """
    timestamps = [datetime(2024, 1, 1) + timedelta(minutes=5 * i)
                  for i in range(num_points)]

    # 根据不同的指标类型生成不同特征的数据
    if metric_type == "cpu":
        return generate_cpu_usage_data(num_points, anomaly_percentage)

    elif metric_type == "memory":
        # 内存使用率特征：基础负载较高，波动较小
        base = 60  # 基础内存使用率
        daily_pattern = 5 * \
                        np.sin(2 * np.pi * np.arange(num_points) / (24 * 12))
        noise = np.random.normal(0, 2, size=num_points)  # 内存波动通常小于CPU
        values = base + daily_pattern + noise

        # 内存泄漏模式：持续增长直到某个点
        labels = np.zeros(num_points, dtype=int)
        anomaly_indices = []

        # 内存泄漏异常
        leak_starts = np.random.choice(
            range(num_points // 2), size=3, replace=False)
        for start in leak_starts:
            duration = np.random.randint(40, 80)
            end = min(start + duration, num_points)

            # 持续增长直到接近100%
            current = values[start]
            values[start:end] = np.linspace(
                current, 95, end - start) + np.random.normal(0, 1, end - start)

            # 模拟内存回收或OOM后重启
            if end < num_points:
                values[end:end + 3] = np.linspace(values[end - 1], base, 3)

            labels[start:end] = 1
            anomaly_indices.extend(range(start, end))

    elif metric_type == "network":
        # 网络流量特征：有明显的工作时间和非工作时间差异，周期性强
        base_load = np.zeros(num_points)
        for i in range(num_points):
            dt = timestamps[i]
            hour = dt.hour
            is_weekend = dt.weekday() >= 5

            if is_weekend:
                base_load[i] = 15  # 周末流量低
            else:
                if 9 <= hour < 18:
                    base_load[i] = 50  # 工作时间流量高
                else:
                    base_load[i] = 20  # 非工作时间流量低

        # 小时级别波动
        hourly_pattern = 10 * np.sin(2 * np.pi * np.arange(num_points) / 12)
        noise = np.random.normal(0, 5, size=num_points)
        values = base_load + hourly_pattern + noise

        labels = np.zeros(num_points, dtype=int)
        anomaly_indices = []

        # 网络风暴
        storm_starts = np.random.choice(
            range(num_points - 10), size=5, replace=False)
        for start in storm_starts:
            duration = np.random.randint(5, 15)
            end = min(start + duration, num_points)
            values[start:end] = np.random.uniform(80, 100, end - start)
            labels[start:end] = 1
            anomaly_indices.extend(range(start, end))

        # 网络中断
        outage_starts = np.random.choice(
            list(set(range(num_points - 5)) - set(anomaly_indices)),
            size=3,
            replace=False
        )
        for start in outage_starts:
            duration = np.random.randint(3, 8)
            end = min(start + duration, num_points)
            values[start:end] = np.random.uniform(0, 2, end - start)
            labels[start:end] = 1
            anomaly_indices.extend(range(start, end))

    elif metric_type == "disk_io":
        # 磁盘IO特征：基础负载低，偶尔有高IO突发
        base = 20
        noise = np.random.normal(0, 3, size=num_points)
        # 小时波动
        hourly_pattern = 5 * np.sin(2 * np.pi * np.arange(num_points) / 12)
        values = base + hourly_pattern + noise

        labels = np.zeros(num_points, dtype=int)
        anomaly_indices = []

        # 高IO活动
        high_io_starts = np.random.choice(
            range(num_points - 10), size=8, replace=False)
        for start in high_io_starts:
            duration = np.random.randint(3, 10)
            end = min(start + duration, num_points)
            peak = np.random.uniform(70, 95)
            # 快速上升然后缓慢下降
            rise = int(duration * 0.3)
            fall = duration - rise

            values[start:start + rise] = np.linspace(values[start], peak, rise)
            if fall > 0:
                values[start + rise:end] = np.linspace(
                    peak, values[min(end, num_points - 1)], fall)

            labels[start:end] = 1
            anomaly_indices.extend(range(start, end))

    else:
        raise ValueError(f"未知的指标类型: {metric_type}")

    # 确保所有值在0-100范围内
    values = np.clip(values, 0, 100)

    # 确保异常索引唯一且排序
    anomaly_indices = sorted(list(set(anomaly_indices)))

    return pd.DataFrame({
        "timestamp": timestamps,
        "value": values,
        "label": labels
    }), anomaly_indices
