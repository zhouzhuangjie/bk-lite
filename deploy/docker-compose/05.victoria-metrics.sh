source "./common.sh"

log "INFO" "创建VictoriaMetrics卷..."
docker volume create victoria-metrics

log "INFO" "启动VictoriaMetrics..."
docker run -itd --name victoria-metrics --restart always \
        -v victoria-metrics:/victoria-metrics-data \
        -p 8428:8428 \
        --network $DOCKER_NETWORK  \
        $DOCKER_IMAGE_VICTORIA_METRICS \
            --storageDataPath=/victoria-metrics-data \
            --httpListenAddr=0.0.0.0:8428 \
            --retentionPeriod=168h  \
            -maxLabelsPerTimeseries=300