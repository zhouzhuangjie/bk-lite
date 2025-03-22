source "./common.sh"

log "INFO" “创建系统管理数据库...”
docker exec -it postgres psql -U postgres -c "CREATE DATABASE system_mgmt"


log "INFO" "启动系统管理服务..."
docker run --name system-manager \
    -it --rm  \
    -e NATS_SERVERS=nats://$NATS_USERNAME:$NATS_PASSWORD@nats:4222 \
    -e NATS_NAMESPACE=system_mgmt \
    -e DEFAULT_REQUEST_TIMEOUT=$DEFAULT_REQUEST_TIMEOUT \
    -e DB_NAME=system_mgmt \
    -e CLIENT_ID=system-manager \
    -e KEYCLOAK_URL_API=$KEYCLOAK_HOSTNAME \
    -e KEYCLOAK_REALM=lite \
    -e KEYCLOAK_CLIENT_ID=lite \
    -e KEYCLOAK_ADMIN_USERNAME=$KEYCLOAK_USERNAME \
    -e KEYCLOAK_ADMIN_PASSWORD=$KEYCLOAK_PASSWORD \
    -e DEBUG=0 \
    -e SECRET_KEY=$SECRET_KEY \
    -e IS_USE_CELERY=True \
    -e DB_USER=$POSTGRES_USERNAME \
    -e DB_HOST=postgres \
    -e DB_PASSWORD=$POSTGRES_PASSWORD \
    -e DB_PORT=5432 \
    --entrypoint "/bin/bash" \
    -v $(pwd)/keycloak_web_secret.env:/tmp/keycloak_web_secret.env \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_SYSTEM_MANAGER -c "python manage.py init_realm && python manage.py init_realm_resource" 

docker run --name system-manager \
    -itd --restart always \
    -e NATS_SERVERS=nats://$NATS_USERNAME:$NATS_PASSWORD@nats:4222 \
    -e NATS_NAMESPACE=system_mgmt \
    -e DEFAULT_REQUEST_TIMEOUT=$DEFAULT_REQUEST_TIMEOUT \
    -e DB_NAME=system_mgmt \
    -e CLIENT_ID=system-manager \
    -e KEYCLOAK_URL_API=$KEYCLOAK_HOSTNAME \
    -e KEYCLOAK_REALM=lite \
    -e KEYCLOAK_CLIENT_ID=lite \
    -e KEYCLOAK_ADMIN_USERNAME=$KEYCLOAK_USERNAME \
    -e KEYCLOAK_ADMIN_PASSWORD=$KEYCLOAK_PASSWORD \
    -e DEBUG=0 \
    -e SECRET_KEY=$SECRET_KEY \
    -e IS_USE_CELERY=True \
    -e DB_USER=$POSTGRES_USERNAME \
    -e DB_HOST=postgres \
    -e DB_PASSWORD=$POSTGRES_PASSWORD \
    -e DB_PORT=5432 \
    -v $(pwd)/keycloak_web_secret.env:/tmp/keycloak_web_secret.env \
    --network $DOCKER_NETWORK \
    $DOCKER_IMAGE_SYSTEM_MANAGER
