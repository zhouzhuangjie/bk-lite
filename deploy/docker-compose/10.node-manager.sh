source "./common.sh"

log "INFO" "创建节点管理数据库..."
docker exec -it postgres psql -U postgres -d postgres -c "CREATE DATABASE node_mgmt"

log "INFO" "启动节点管理..."
docker run --name node-manager \
		-itd \
		-e NATS_SERVERS=nats://$NATS_USERNAME:$NATS_PASSWORD@nats:4222 \
		-e NATS_NAMESPACE=node_mgmt \
		-e DB_NAME=node_mgmt \
		-e CLIENT_ID=node_mgmt \
		-e SIDECAR_INIT_TOKEN=$SIDECAR_INIT_TOKEN \
		-e DEFAULT_ZONE_VAR_KAFKA_HOST=$HOST_IP \
		-e DEFAULT_ZONE_VAR_KAFKA_PORT=9092 \
		-e DEFAULT_ZONE_VAR_KAFKA_METRICS_TOPIC=metrics \
		-e DEFAULT_ZONE_VAR_KAFKA_USERNAME=$KAFKA_USERNAME \
		-e DEFAULT_ZONE_VAR_KAFKA_PASSWORD=$KAFKA_PASSWORD \
		-e DEFAULT_ZONE_VAR_NATS_SERVERS=nats://$HOST_IP:4222 \
		-e DEFAULT_ZONE_VAR_NATS_USERNAME=$NATS_USERNAME \
		-e DEFAULT_ZONE_VAR_NATS_PASSWORD=$NATS_PASSWORD \
		-e SIDECAR_INPUT_MODE=nats \
		-e DEBUG=0 \
		-e SECRET_KEY=$SECRET_KEY \
		-e IS_USE_CELERY=False \
		-e DB_USER=postgres \
		-e DB_HOST=postgres \
		-e DB_PASSWORD=postgres \
		-e DB_PORT=5432 \
		--network $DOCKER_NETWORK \
		$DOCKER_IMAGE_NODE_MANAGER

log "INFO" "启动节点管理Web..."
docker run --name node-manager-web \
		-itd --restart always \
		-e KEYCLOAK_CLIENT_ID=lite \
		-e KEYCLOAK_CLIENT_SECRET=$KEYCLOAK_WEB_CLIENT_SECRET \
		-e KEYCLOAK_ISSUER=$KEYCLOAK_HOSTNAME/realms/lite \
		-e NEXTAUTH_URL=http://$HOST_IP:20001 \
		-e NEXTAUTH_SECRET=$NEXTAUTH_SECRET \
		-e NEXTAPI_URL=http://node-manager:8000 \
		--network $DOCKER_NETWORK \
		--label "traefik.enable=true" \
  		--label "traefik.http.routers.node-manager-web.rule=Host(\`$HOST_IP\`)" \
  		--label "traefik.http.routers.node-manager-web.entrypoints=node-manager-web" \
  		--label "traefik.http.services.node-manager-web.loadbalancer.server.port=3000" \
		$DOCKER_IMAGE_NODE_MANAGER_WEB