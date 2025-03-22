#!/bin/bash
# 引入配置
source "${BASE_DIR}/scripts/config.sh"

# 彩色日志输出
log() {
  local level=$1
  local msg=$2
  local timestamp=$(date +"%Y-%m-%d %T")
  local color=""
  
  case "$level" in
    "DEBUG") color="\033[34m" ;;
    "INFO") color="\033[32m" ;;
    "WARN") color="\033[33m" ;;
    "ERROR") color="\033[31m" ;;
  esac

  declare -A log_levels=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3)
  [[ ${log_levels[$level]} -ge ${log_levels[$LOG_LEVEL]} ]] || return

  echo -e "${color}[${timestamp}] [${level}] ${msg}\033[0m"
}

# 错误处理
die() {
  log "ERROR" "$1"
  exit "${2:-1}"
}

# 环境变量校验
validate_env_vars() {
  for var in "$@"; do
    if [ -z "${!var:-}" ]; then
      die "Environment variable $var is required but not set"
    fi
  done
}