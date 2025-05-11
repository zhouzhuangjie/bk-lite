import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def visualize_anomaly_detection_results(test_df, y_pred, anomaly_indices, window_offset, detector,
                                        title="异常检测结果",
                                        output_path="./test_results/anomaly_detection_result.png"):
    """
    可视化异常检测结果，对比预测结果和人工异常标注
    参数:
        test_df: 测试数据DataFrame，包含timestamp和value列
        y_pred: 模型的预测结果数组
        anomaly_indices: 人为标记的异常点索引
        window_offset: 模型在时间窗口上的偏移
        detector: 检测器对象，提供评估方法
        title: 图形标题
        output_path: 保存图像的路径
    """
    # 扩展预测结果到整个时间长度
    full_predictions = np.zeros(len(test_df), dtype=int)
    if len(y_pred) + window_offset <= len(full_predictions):
        full_predictions[window_offset:window_offset + len(y_pred)] = y_pred
    else:
        print(f"警告: 截断预测结果！")
        valid_len = len(test_df) - window_offset
        full_predictions[window_offset:window_offset + valid_len] = y_pred[:valid_len]
    # 绘制时序数据和异常检测结果
    plt.figure(figsize=(14, 6))
    plt.plot(test_df['timestamp'], test_df['value'], label='时序数据')
    # 标记预测异常点
    predicted_anomalies = test_df[full_predictions == 1]
    plt.scatter(predicted_anomalies['timestamp'], predicted_anomalies['value'],
                color='red', marker='o', s=50, label='预测异常点')
    # 标记人工设置的异常点
    plt.scatter(test_df.iloc[anomaly_indices]['timestamp'], test_df.iloc[anomaly_indices]['value'],
                color='green', marker='x', s=80, label='实际异常点')
    plt.title(title)
    plt.xlabel('时间')
    plt.ylabel('CPU 负载')
    plt.legend()
    plt.tight_layout()
    # 保存图片
    plt.savefig(output_path)
    print(f"异常检测结果图保存到: {output_path}")
    # 评估性能指标
    y_true = np.zeros(len(test_df), dtype=int)
    y_true[anomaly_indices] = 1
    valid_len = min(len(y_pred), len(test_df) - window_offset)
    metrics = detector.evaluate(y_true[window_offset:window_offset + valid_len], y_pred[:valid_len])
    print(f"性能指标 - Precision: {metrics['precision']:.4f}, Recall: {metrics['recall']:.4f}, F1: {metrics['f1']:.4f}")
    return metrics

def generate_test_data_with_indices(num_points=None):
    """
    生成高级模拟的测试数据并返回异常索引
    """
    if num_points is None:
        num_points = 24 * 60  # 默认模拟一天（一分钟一个数据点）

    # 生成时间戳
    timestamps = [datetime(2024, 1, 2) + timedelta(minutes=i)
                  for i in range(num_points)]

    # 正常基线值
    base = 30
    period1, period2, period3 = 24 * 60, 60, 300
    cycle = (
        10 * np.sin(2 * np.pi * np.arange(num_points) / period1) +
        7 * np.sin(2 * np.pi * np.arange(num_points) / period2) +
        3 * np.sin(2 * np.pi * np.arange(num_points) / period3)
    )
    noise = np.random.normal(0, 7, size=num_points)
    values = base + cycle + noise
    values = np.clip(values, 0, 100)

    labels = np.zeros(num_points, dtype=int)  # 初始化标签

    # 异常类型索引记录
    anomaly_indices = []

    # 边界异常
    borderline_indices = np.random.choice(num_points, size=20, replace=False)
    values[borderline_indices] += np.random.uniform(10, 15, size=20)
    labels[borderline_indices] = 1
    anomaly_indices.extend(borderline_indices.tolist())

    # 过渡型异常
    transition_start = np.random.choice(list(set(range(100, num_points - 30))), size=5, replace=False)
    for start in transition_start:
        values[start:start + 30] = np.linspace(30, 80, 30)
        labels[start:start + 30] = 1
        anomaly_indices.extend(range(start, start + 30))

    # 隐匿峰值
    hidden_spike_indices = np.random.choice(list(set(range(100, num_points))), size=15, replace=False)
    values[hidden_spike_indices] = np.random.uniform(70, 80, size=15)
    labels[hidden_spike_indices] = 1
    anomaly_indices.extend(hidden_spike_indices.tolist())

    # 周期性抖动
    jitter_start = np.random.choice(list(set(range(100, num_points - 20))), size=8, replace=False)
    for start in jitter_start:
        jitter_vals = base + np.random.choice([20, 60], size=10)
        values[start:start + 10] = jitter_vals
        labels[start:start + 10] = 1
        anomaly_indices.extend(range(start, start + 10))

    # 持续微小波动
    subtle_wave_start = np.random.choice(list(set(range(100, num_points - 50))), size=8, replace=False)
    for start in subtle_wave_start:
        subtle_wave = base + 5 * np.cos(2 * np.pi * np.arange(50) / 25) + np.random.normal(0, 2, size=50)
        values[start:start + 50] = subtle_wave
        labels[start:start + 50] = 1
        anomaly_indices.extend(range(start, start + 50))

    # 干扰型异常
    intermittent_anomalies = np.random.choice(list(set(range(100, num_points))), size=12, replace=False)
    values[intermittent_anomalies] = np.random.uniform(50, 90, size=12)
    labels[intermittent_anomalies] = 1
    anomaly_indices.extend(intermittent_anomalies.tolist())

    anomaly_indices = sorted(set(anomaly_indices))  # 去重并排序
    return pd.DataFrame({"timestamp": timestamps, "value": values, "label": labels}), anomaly_indices


def generate_training_data(num_points=None):
    """
    生成模拟的CPU训练数据，包含多种CPU异常情况
    """
    if num_points is None:
        num_points = 24 * 60  # 默认模拟一天（一分钟一个数据点）
    # 生成时间戳
    timestamps = [datetime(2024, 1, 1) + timedelta(minutes=i)
                  for i in range(num_points)]
    # 正常基线值：非对称周期波动 + 噪声
    base = 30
    period1 = 24 * 60  # 24小时周期（以分钟为单位）
    period2 = 60  # 1小时周期（以分钟为单位）
    cycle = 10 * np.sin(2 * np.pi * np.arange(num_points) / period1) + \
            5 * np.sin(2 * np.pi * np.arange(num_points) / period2)
    noise = np.random.normal(0, 5, size=num_points)
    values = base + cycle + noise
    values = np.clip(values, 0, 100)
    labels = np.zeros(num_points, dtype=int)
    # 1. 过载峰值（Spike Load）
    spike_indices = np.random.choice(num_points, size=30, replace=False)
    values[spike_indices] = np.random.uniform(90, 100, size=30)  # 接近满负载
    labels[spike_indices] = 1
    # 2. 空转低负载（Idle Load）
    idle_indices = np.random.choice(
        list(set(range(num_points)) - set(spike_indices)), size=20, replace=False)
    values[idle_indices] = np.random.uniform(0, 5, size=20)  # 接近空闲
    labels[idle_indices] = 1
    # 3. 高频抖动异常（Cyclic Anomalies）
    jitter_start = np.random.choice(list(set(range(100, num_points - 20)) - set(spike_indices) - set(idle_indices)),
                                    size=10, replace=False)
    for start in jitter_start:
        jitter_vals = base + np.random.choice([10, 90], size=10)  # 高频随机抖动
        values[start:start + 10] = jitter_vals
        labels[start:start + 10] = 1
    # 4. 缓慢上升异常（Slow Rise）
    rise_start = np.random.choice(list(set(range(100, num_points - 30)) - set(spike_indices) - set(idle_indices)),
                                  size=8, replace=False)
    for start in rise_start:
        values[start:start + 15] = np.linspace(40, 90, 15)  # 缓慢上升
        labels[start:start + 15] = 1
    # 5. 阶跃增加（Step Increase）
    step_start = np.random.choice(list(set(range(100, num_points - 50)) - set(spike_indices) - set(idle_indices)),
                                  size=5, replace=False)
    for start in step_start:
        values[start:start + 20] = np.concatenate([np.full(10, 30), np.full(10, 80)])  # 从稳定低负载到高负载
        labels[start:start + 20] = 1
    # 6. 长时间高负载（Constant High）
    high_start = np.random.choice(list(set(range(num_points - 60)) - set(spike_indices) - set(idle_indices)),
                                  size=5, replace=False)
    for start in high_start:
        values[start:start + 60] = np.random.uniform(85, 95, 60)  # 持续高负载
        labels[start:start + 60] = 1
    # 7. 长时间低负载（Constant Low）
    low_start = np.random.choice(list(set(range(num_points - 60)) - set(spike_indices) - set(idle_indices)),
                                 size=5, replace=False)
    for start in low_start:
        values[start:start + 60] = np.random.uniform(5, 10, 60)  # 持续低负载
        labels[start:start + 60] = 1
    return pd.DataFrame({
        "timestamp": timestamps,
        "value": values,
        "label": labels
    })
