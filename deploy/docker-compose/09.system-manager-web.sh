source "./common.sh"

log "INFO" "启动系统管理Web..."
docker run --name system-manager-web \
    -itd --restart always \
    -e KEYCLOAK_CLIENT_ID=lite \
    -e KEYCLOAK_CLIENT_SECRET=$KEYCLOAK_WEB_CLIENT_SECRET \
    -e KEYCLOAK_ISSUER=$KEYCLOAK_HOSTNAME/realms/lite \
    -e NEXTAUTH_URL=http://$HOST_IP:$TRAEFIK_SYSTEM_MANAGER_PORT \
    -e NEXTAUTH_SECRET=$NEXTAUTH_SECRET \
    -e NEXTAPI_URL=http://system-manager:8000 \
    --network $DOCKER_NETWORK \
    --label "traefik.enable=true" \
    --label "traefik.http.routers.system-manager-web.rule=Host(\`$HOST_IP\`)" \
    --label "traefik.http.routers.system-manager-web.entrypoints=system-manager-web" \
    --label "traefik.http.services.system-manager-web.loadbalancer.server.port=3000" \
    $DOCKER_IMAGE_SYSTEM_MANAGER_WEB