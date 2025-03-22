source "./common.sh"

log "INFO" "创建Postgres数据目录..."
docker volume create postgres

log "INFO" "启动Postgres容器..."
docker run -itd --name postgres --restart always -p 5432:5432 \
    --network $DOCKER_NETWORK \
    -e POSTGRES_USER=$POSTGRES_USERNAME \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -v postgres:/var/lib/postgresql/data \
    $DOCKER_IMAGE_POSTGRES
    