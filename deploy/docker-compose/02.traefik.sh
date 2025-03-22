source "./env.sh"
source "./common.sh"

log "INFO" “启动Traefik容器...”

docker run -itd \
  --name traefik --restart always \
  -p $TRAEFIK_KEYCLOAK_PORT:$TRAEFIK_KEYCLOAK_PORT \
  -p $TRAEFIK_SYSTEM_MANAGER_PORT:$TRAEFIK_SYSTEM_MANAGER_PORT \
  -p $TRAEFIK_NODE_MANAGER_PORT:$TRAEFIK_NODE_MANAGER_PORT \
  -p $TRAEFIK_MONITOR_PORT:$TRAEFIK_MONITOR_PORT \
  -p $TRAEFIK_DASHBOARD_PORT:$TRAEFIK_DASHBOARD_PORT \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/conf/traefik/dynamic.yml:/etc/traefik/dynamic.yml \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.traefik-dashboard.rule=Host(\`$HOST_IP\`)" \
  --label "traefik.http.routers.traefik-dashboard.entrypoints=traefik-dashboard" \
  --label "traefik.http.services.traefik-dashboard.loadbalancer.server.port=8080" \
  --network $DOCKER_NETWORK \
  $DOCKER_IMAGE_TRAEFIK \
    --log.level=INFO \
    --api.insecure=true \
    --api.dashboard=$TRAEFIK_ENABLE_DASHBOARD \
    --providers.docker.endpoint=unix:///var/run/docker.sock \
    --providers.docker.exposedByDefault=false \
    --providers.file.filename=/etc/traefik/dynamic.yml \
    --providers.file.watch=true \
    --accesslog \
    --entrypoints.keycloak.address=:$TRAEFIK_KEYCLOAK_PORT \
    --entrypoints.system-manager-web.address=:$TRAEFIK_SYSTEM_MANAGER_PORT \
    --entrypoints.node-manager-web.address=:$TRAEFIK_NODE_MANAGER_PORT \
    --entrypoints.monitor-web.address=:$TRAEFIK_MONITOR_PORT \
    --entrypoints.traefik-dashboard.address=:$TRAEFIK_DASHBOARD_PORT