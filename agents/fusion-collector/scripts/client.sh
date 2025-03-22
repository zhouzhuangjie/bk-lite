#!/bin/bash
source "${BASE_DIR}/scripts/config.sh"
source "${BASE_DIR}/scripts/common.sh"

run_client_mode() {
  log "INFO" "Initializing client mode"
  validate_env_vars SERVER_URL SERVER_API_TOKEN

  log "INFO" "Generating sidecar configuration"
  cat > "$SIDECAR_CONF" <<EOF
server_url: "${SERVER_URL}"
server_api_token: "${SERVER_API_TOKEN}"
node_id: "file:${BASE_DIR}/node-id"
node_name: ""
update_interval: 10
tls_skip_verify: false
send_status: true
list_log_files: []
cache_path: "${BASE_DIR}/cache"
log_path: "${BASE_DIR}/log"
log_rotate_max_file_size: "10MiB"
log_rotate_keep_files: 10
collector_validation_timeout: "1m"
collector_shutdown_timeout: "10s"
collector_configuration_directory: "${BASE_DIR}/generated"

tags:
  - proxy

collector_binaries_accesslist:
  - "${BASE_DIR}/bin/*"
EOF

  log "INFO" "Starting collector-sidecar"
  exec "${BASE_DIR}/collector-sidecar" -c "$SIDECAR_CONF"
}

run_client_mode