#!/bin/bash

# ANSI escape codes for colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log messages with colored output
#
# This function logs messages with a timestamp and a specified log level.
# It supports different colors for different log levels:
# - INFO: Blue
# - WARNING: Yellow
# - ERROR: Red
# - SUCCESS: Green
#
# Usage:
# log "INFO" "This is an informational message."
# log "WARNING" "This is a warning message."
# log "ERROR" "This is an error message."
# log "SUCCESS" "This is a success message."
#
# Parameters:
# $1: The log level (INFO, WARNING, ERROR, SUCCESS).
# $2: The message to be logged.
log() {
    local level="$1"
    local message="$2"
    local color=""

    case "$level" in
        "INFO")
            color="$BLUE"
            ;;
        "WARNING")
            color="$YELLOW"
            ;;
        "ERROR")
            color="$RED"
            ;;
        "SUCCESS")
            color="$GREEN"
            ;;
        *)
            color="$NC"
            ;;
    esac

    echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# Function to validate environment variables
#
# This function checks if a given environment variable is set.
# If the variable is not set, it logs an error message and exits the script with a status code of 1.
#
# Usage:
# validate_env_var "DOCKER_NETWORK"
# validate_env_var "API_KEY"
#
# Parameters:
# $1: The name of the environment variable to validate.
validate_env_var() {
    local var_name="$1"
    if [ -z "${!var_name}" ]; then
        log "ERROR" "Environment variable $var_name is not set."
        exit 1
    fi
}


# 导入环境变量
if [ -f default.env ]; then
    # 从default.env文件中加载环境变量
    export $(grep -v '^#' default.env | xargs)
else
    log "ERROR" ".env文件未找到，请检查。"
    exit 1
fi

if [ -f keycloak_web_secret.env ]; then
    export $(grep -v '^#' keycloak_web_secret.env | xargs)
fi