source "./common.sh"

log "INFO" “创建KeyCloak数据库...”
docker exec -it postgres psql -U postgres -c "CREATE DATABASE keycloak"

log "INFO" “启动KeyCloak...”
docker run --name keycloak \
    -itd \
    -e KC_DB=postgres \
    -e KC_HOSTNAME=$KEYCLOAK_HOSTNAME \
    -e KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak \
    -e KC_DB_USERNAME=$POSTGRES_USERNAME \
    -e KC_DB_PASSWORD=$POSTGRES_PASSWORD \
    -e KC_BOOTSTRAP_ADMIN_USERNAME=$KEYCLOAK_USERNAME \
    -e KC_BOOTSTRAP_ADMIN_PASSWORD=$KEYCLOAK_PASSWORD \
    -e KC_PROXY_HEADERS=forwarded \
    -e KC_HOSTNAME_STRICT=false \
    -e KC_HTTP_ENABLED=true \
    --label "traefik.enable=true" \
    --label "traefik.http.routers.keycloak.rule=Host(\`$HOST_IP\`)" \
    --label "traefik.http.routers.keycloak.entrypoints=keycloak" \
    --label "traefik.http.services.keycloak.loadbalancer.server.port=8080" \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_KEYCLOAK start

# 循环检查 Keycloak 是否成功启动
MAX_ATTEMPTS=120  # 最大尝试次数
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" $KEYCLOAK_HOSTNAME)
    if [ $RESPONSE_CODE -eq 302 ]; then
        log "INFO" "Keycloak 已成功启动。"
        break
    else
        log "INFO" "Keycloak 尚未启动，第 $((ATTEMPT + 1)) 次尝试，等待 1 秒后继续检查..."
        sleep 1
    fi
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    log "ERROR" "经过 $MAX_ATTEMPTS 次尝试，Keycloak 仍未成功启动。"
fi    