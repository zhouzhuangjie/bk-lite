#!/bin/bash
source "./scripts/config.sh"
source "./scripts/common.sh"

generate_telegraf_config() {
  log "INFO" "Generating Telegraf configuration"
  cat > "$TELEGRAF_CONF" <<EOF
[global_tags]

[agent]
  interval = "5s"
  round_interval = true
  metric_buffer_limit = 100000
  flush_buffer_when_full = true
  collection_jitter = "0s"
  flush_interval = "2s"
  flush_jitter = "0s"
  debug = false
  quiet = false

EOF

  case "$METRIC_INPUT" in
    "kafka")
      validate_env_vars METRIC_KAFKA_BROKERS METRIC_KAFKA_SASL_USERNAME METRIC_KAFKA_SASL_PASSWORD
      cat >> "$TELEGRAF_CONF" <<EOF
[[inputs.kafka_consumer]]
  brokers = ["${METRIC_KAFKA_BROKERS}"]
  topics = ["${METRIC_KAFKA_TOPIC}"]
  sasl_username = "${METRIC_KAFKA_SASL_USERNAME}"
  sasl_password = "${METRIC_KAFKA_SASL_PASSWORD}"
  sasl_mechanism = "PLAIN"
  offset = "newest"

EOF
      ;;
    "http")
      cat >> "$TELEGRAF_CONF" <<EOF
[[inputs.http_listener_v2]]
  service_address = ":8080"
  read_timeout = "10s"
  write_timeout = "10s"
  max_body_size = "32MiB"

EOF
      ;;
    "nats")
      validate_env_vars METRIC_NATS_SERVERS METRIC_NATS_USERNAME METRIC_NATS_PASSWORD
      cat >> "$TELEGRAF_CONF" <<EOF
[[inputs.nats_consumer]]
  servers = ["${METRIC_NATS_SERVERS}"]
  jetstream_subjects = ["metrics.*"]
  queue_group = "metrics_consumers"
  data_format = "influx"
  username = "${METRIC_NATS_USERNAME}"
  password = "${METRIC_NATS_PASSWORD}"
EOF
      ;;
    *) die "Invalid METRIC_INPUT. Supported: 'kafka', 'http', 'nats'" ;;
  esac

  case "$METRIC_OUTPUT" in
    "influx")
      validate_env_vars METRIC_OUTPUT_URL
      cat >> "$TELEGRAF_CONF" <<EOF
[[outputs.influxdb]]
  urls = ["${METRIC_OUTPUT_URL}"]
  database = "victoriametrics"
  skip_database_creation = true
  exclude_retention_policy_tag = true
  content_encoding = "gzip"
EOF
      ;;
    "debug")
      cat >> "$TELEGRAF_CONF" <<EOF
[[outputs.file]]
  files = ["stdout"]
EOF
      ;;
    *) die "Invalid METRIC_OUTPUT. Supported: 'influx', 'debug'" ;;
  esac
}

run_metric_server() {
  log "INFO" "Initializing Metric Server (Telegraf)"
  generate_telegraf_config
  log "INFO" "Starting Telegraf with ${TELEGRAF_CONF}"
  exec "${BASE_DIR}/bin/telegraf" -config "$TELEGRAF_CONF"
}

run_metric_server