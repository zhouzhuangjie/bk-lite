source "./env.sh"
source "./common.sh"

log "INFO" "创建监控系统数据库..."
docker exec -it postgres psql -U postgres -d postgres -c "CREATE DATABASE monitor"

log "INFO" "启动监控系统..."
docker run --name monitor \
    -itd \
    -e NATS_SERVERS=nats://$NATS_USERNAME:$NATS_PASSWORD@nats:4222 \
    -e NATS_NAMESPACE=monitor \
    -e CLIENT_ID=monitor \
    -e DB_NAME=monitor \
    -e VICTORIAMETRICS_HOST="http://victoria-metrics:8428" \
    -e IS_USE_CELERY="True" \
    -e BROKER_URL="redis://:$REDIS_PASSWORD@redis:6379/10" \
    -e CELERY_BROKER_URL="redis://:$REDIS_PASSWORD@redis:6379/10" \
    -e CELERY_RESULT_BACKEND="redis://:$REDIS_PASSWORD@redis:6379/10" \
    -e DEBUG=0 \
    -e SECRET_KEY=$SECRET_KEY \
    -e DB_USER=$POSTGRES_USERNAME \
    -e DB_HOST=postgres \
    -e DB_PASSWORD=$POSTGRES_PASSWORD \
    -e DB_PORT=5432 \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_MONITOR

log "INFO" "启动监控系统Web..."
docker run --name monitor-web \
    -itd --restart always \
    -e KEYCLOAK_CLIENT_ID=$KEYCLOAK_WEB_CLIENT \
    -e KEYCLOAK_CLIENT_SECRET=$KEYCLOAK_WEB_CLIENT_SECRET \
    -e KEYCLOAK_ISSUER=$KEYCLOAK_HOSTNAME/realms/lite \
    -e NEXTAUTH_URL=http://$HOST_IP:$TRAEFIK_MONITOR_PORT \
    -e NEXTAUTH_SECRET=$NEXTAUTH_SECRET \
    -e NEXTAPI_URL=http://monitor:8000 \
    --network $DOCKER_NETWORK \
    --label "traefik.enable=true" \
    --label "traefik.http.routers.monitor-web.rule=Host(\`$HOST_IP\`)" \
    --label "traefik.http.routers.monitor-web.entrypoints=monitor-web" \
    --label "traefik.http.services.monitor-web.loadbalancer.server.port=3000" \
    $DOCKER_IMAGE_MONITOR_WEB