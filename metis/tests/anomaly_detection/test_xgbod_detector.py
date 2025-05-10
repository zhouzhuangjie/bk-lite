import pytest
from src.anomaly_detection.xgbod_detector import XGBODDetector
from tests.anomaly_detection.utils import generate_training_data, generate_test_data, \
    visualize_anomaly_detection_results
from loguru import logger



@pytest.fixture
def setup_detector(tmp_path):
    """准备检测器：生成训练数据并训练模型"""
    # 生成训练数据
    train_df = generate_training_data()

    # 保存到临时文件
    file_path = tmp_path / "train.csv"
    train_df.to_csv(file_path, index=False)

    # 初始化和训练检测器
    detector = XGBODDetector()
    detector.train({
        "csv_files": [str(file_path)],
        "freq": "1min",  # 更新为1分钟频率
        "window": 30,  # 更新窗口大小，使其包含更多点以覆盖相似的时间范围
        "test_size": 0.2,
        "val_size": 0.1,
        "n_estimators": 100
    })
    return detector


def test_model_evaluation(setup_detector):
    """测试训练后的模型在测试集上的性能"""
    detector = setup_detector

    X_test, y_test = detector.test_data
    y_pred = detector.predict(X_test)

    # 评估测试数据上的性能
    test_metrics = detector.evaluate(y_test, y_pred)
    logger.info("Test metrics:", test_metrics)


def test_external_prediction(setup_detector):
    """测试模型在外部数据集上的预测能力"""
    detector = setup_detector

    # 生成测试数据
    test_df, anomaly_indices = generate_test_data()

    # 处理数据并进行预测，使用1分钟的频率与训练一致
    X_new = detector.process_external_data(test_df, freq="1min", window=30)
    y_new_pred = detector.predict(X_new)

    logger.info(f"异常检测结果:[{y_new_pred}]")

    # 使用通用可视化函数进行结果展示和评估
    visualize_anomaly_detection_results(
        test_df=test_df,
        y_pred=y_new_pred,
        anomaly_indices=anomaly_indices,
        window_offset=30-1,  # 默认窗口大小-1
        detector=detector,
        title='XGBOD 异常检测结果 (1min频率)',
        output_path='./test_results/xgbod_anomaly_detection_result.png'
    )
