from loguru import logger

from src.anomaly_detection.suod_detector import SuodDetector
from src.anomaly_detection.xgbod_detector import XGBODDetector
from tests.anomaly_detection.utils import (
    generate_training_data,
    generate_test_data_with_indices,
)


def test_suod_detector():
    detector = SuodDetector()
    detector_workflow(detector, 'sudo', train_config={
        "freq": "infer",
        "window": 30,
        'hyper_params': {
        }
    })


def test_xgbod_detector():
    detector = XGBODDetector()
    detector_workflow(detector, 'xgbod', train_config={
        "freq": "infer",
        "window": 30,
        'hyper_params': {
            'n_estimators': 1000,
        }
    })


def detector_workflow(detector, job_name, train_config):
    """
    测试整个异常检测流程，包括模型训练、评估及外部测试数据预测。
    """
    # Step 1: 生成训练数据并保存到文件
    train_df = generate_training_data()
    train_file_path = f"./test_results/anomaly_detection_train_{job_name}.csv"
    train_df.to_csv(train_file_path, index=False)
    train_config['train_data_path'] = train_file_path
    logger.info("开始训练模型...")
    detector.train(
        train_config=train_config
    )
    logger.info("模型训练完成。")

    # Step 3: 评估模型性能
    logger.info("开始评估模型性能...")
    evaluate_result = detector.evaluate_model()
    logger.info(
        f"""
        模型评估结果:
            Accuracy:  {evaluate_result['accuracy']:.4f}
            Precision: {evaluate_result['precision']:.4f}
            Recall:    {evaluate_result['recall']:.4f}
            F1-score:  {evaluate_result['f1']:.4f}
        """
    )

    # Step 4: 保存模型
    model_file_path = f"./test_results/{job_name}_model.pkl"
    detector.save_model(model_file_path)

    # Step 5: 生成测试数据
    test_df, anomaly_indices = generate_test_data_with_indices()
    test_file_path = f"./test_results/anomaly_detection_test_{job_name}.csv"
    test_df.to_csv(test_file_path, index=False)

    # Step 6: 加载模型进行外部预测
    logger.info("加载训练好的模型...")
    detector.load_model(model_file_path)
    logger.info("开始进行外部数据的预测...")
    predict_result = detector.predict(test_df)

    # Step 7: 可视化预测结果并计算性能指标
    logger.info("可视化预测结果并计算性能指标...")
    metrics = detector.visualize_anomaly_detection_results(
        test_df=test_df,
        y_pred=predict_result["anomaly"].values,  # 提取预测结果列
        title="外部预测测试 - 异常检测结果",
        output_path=f"./test_results/anomaly_detection_test_results_{job_name}.png",
    )

    # Step 8: 打印性能指标
    logger.info(
        f"""
        外部预测性能评估结果:
            Precision: {metrics['precision']:.4f}
            Recall:    {metrics['recall']:.4f}
            F1 Score:  {metrics['f1']:.4f}
        """
    )
