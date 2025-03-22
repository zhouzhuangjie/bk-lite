source "./env.sh"
source "./common.sh"

log "INFO" "启动Fusion Collectors 服务端"
docker run -itd --name fusion-collectior-server \
    -e RUN_MODE=metric_server \
    -e METRIC_INPUT=nats \
    -e METRIC_NATS_SERVERS=nats://nats:4222 \
    -e METRIC_NATS_USERNAME=$NATS_USERNAME \
    -e METRIC_NATS_PASSWORD=$NATS_PASSWORD \
    -e METRIC_OUTPUT=influx \
    -e METRIC_OUTPUT_URL=http://victoria-metrics:8428 \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_FUSION_COLLECTOR	

log "INFO" "启动Fusion Collectors 客户端"
docker run -itd --name fusion-collectior-client \
    -e RUN_MODE=client \
    -e SERVER_URL=http://node-manager:8000/node_mgmt/open_api/node \
    -e SERVER_API_TOKEN=$SIDECAR_INIT_TOKEN \
    --network $DOCKER_NETWORK \
    --hostname fusion-collectior-client \
    $DOCKER_IMAGE_FUSION_COLLECTOR