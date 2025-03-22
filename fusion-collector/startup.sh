#!/bin/bash
set -euo pipefail

# 加载配置和公共函数
BASE_DIR="/opt/fusion-collectors"
source "${BASE_DIR}/scripts/config.sh"
source "${BASE_DIR}/scripts/common.sh"

case "$RUN_MODE" in
  "metric_server") exec "${BASE_DIR}/scripts/metric_server.sh" ;;
  "client")        exec "${BASE_DIR}/scripts/client.sh" ;;
  "log_server")    die "Log Server mode not implemented" 3 ;;
  "trace_server")  die "Trace Server mode not implemented" 3 ;;
  *)               die "Invalid RUN_MODE: $RUN_MODE" 2 ;;
esac