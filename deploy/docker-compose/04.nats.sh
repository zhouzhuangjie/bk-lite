source "./common.sh"

log "INFO" "创建NATS卷..."
docker volume create nats

log "INFO" "启动NATS..."
docker run -itd --name nats \
    -v $(pwd)/conf/nats/nats.conf:/etc/nats/nats.conf \
    -v nats:/nats \
    --restart always \
    -p 4222:4222 \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_NATS \
        -c /etc/nats/nats.conf  --user $NATS_USERNAME --pass $NATS_PASSWORD

log "INFO" "创建JetStream..."
docker run --rm --name natscli \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_NATS_CLI -s nats://nats:4222 \
    --user $NATS_USERNAME --password $NATS_PASSWORD \
        stream add metrics --subjects=metrics.* --storage=file \
        --replicas=1 --retention=limits  --discard=old \
        --max-age=20m --max-bytes=104857600 --max-consumers=-1 \
        --max-msg-size=-1 --max-msgs=-1 --max-msgs-per-subject=1000000 \
        --dupe-window=5m --no-allow-rollup --no-deny-delete --no-deny-purge 