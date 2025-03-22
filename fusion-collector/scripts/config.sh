#!/bin/bash

# ==================================================
# 常量定义
# ==================================================
export BASE_DIR="/opt/fusion-collectors"
export TELEGRAF_CONF="${BASE_DIR}/telegraf.conf"
export SIDECAR_CONF="${BASE_DIR}/sidecar.yml"

# ==================================================
# 环境变量默认值
# ==================================================
# 运行模式
export RUN_MODE=${RUN_MODE:-"client"}  # client/metric_server/log_server/trace_server

# 服务器相关配置
export SERVER_URL=${SERVER_URL:-""}
export SERVER_API_TOKEN=${SERVER_API_TOKEN:-""}

# 指标输入输出配置
export METRIC_INPUT=${METRIC_INPUT:-""}
export METRIC_OUTPUT=${METRIC_OUTPUT:-"influx"}  # influx/debug
export METRIC_OUTPUT_URL=${METRIC_OUTPUT_URL:-""}

# Kafka 相关配置
export METRIC_KAFKA_BROKERS=${METRIC_KAFKA_BROKERS:-""}
export METRIC_KAFKA_TOPIC=${METRIC_KAFKA_TOPIC:-"telegraf"}
export METRIC_KAFKA_SASL_USERNAME=${METRIC_KAFKA_SASL_USERNAME:-""}
export METRIC_KAFKA_SASL_PASSWORD=${METRIC_KAFKA_SASL_PASSWORD:-""}

# 日志配置
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}  # DEBUG, INFO, WARN, ERROR