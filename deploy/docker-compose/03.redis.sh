source "./env.sh"
source "./common.sh"

log "INFO" "创建Redis卷..."
docker volume create redis

log "INFO" "启动Redis..."
docker run --name redis -itd  -p 6379:6379 \
        --restart always -v redis:/data \
        --network $DOCKER_NETWORK \
        $DOCKER_IMAGE_REDIS \
            redis-server --requirepass $REDIS_PASSWORD