#!/bin/bash
set -euo pipefail

# 解析命令行参数，长短混合模式
(( $# == 0 )) && exit 1
while (( $# > 0 )); do 
    case "$1" in
        -w | --wan-ip )
            shift
            DOMAIN=$1
            ;;
        -*)
            exit -1
            ;;
        *) 
            break
            ;;
    esac
    shift 
done 
# 参数校验
if [[ -z $DOMAIN ]]; then
    echo "wan-ip is required"
    exit -1
fi
rnd_password() {
    echo $(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
}
# 生成需要的密码环境变量
KEYCLOAK_POSTGRES_PASSWORD=$(rnd_password)
KEYCLOAK_ADMIN_PASSWORD=$(rnd_password)
NATS_ADMIN_PASSWORD=$(rnd_password)
NATS_SERVER_PASSWORD=$(rnd_password)
NATS_CLIENT_PASSWORD=$(rnd_password)
SYSTEM_MANGER_POSTGRES_PASSWORD=$(rnd_password)
SYSTEM_MANGER_KEYCLOAK_SECRET=$(rnd_password)
SYSTEM_MANGER_WEB_NEXT_AUTH_SECRET=$(rnd_password)
# keycloak
if [[ -f postgres/overlays/keycloak/postgres.env ]]; then
    echo "keycloak postgres.env already exists"
else
    cat <<EOF > postgres/overlays/keycloak/postgres.env
POSTGRES_USER=keycloak
POSTGRES_PASSWORD=${KEYCLOAK_POSTGRES_PASSWORD}
EOF
fi

if [[ -f keycloak/overlays/prod/keycloak.env ]]; then
    echo "keyclok.env already exists"
else
    cat <<EOF > keycloak/overlays/prod/keycloak.env
KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
KC_DB_USERNAME=keycloak
KC_DB_PASSWORD=${KEYCLOAK_POSTGRES_PASSWORD}
KC_BOOTSTRAP_ADMIN_USERNAME=admin
KC_BOOTSTRAP_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
KC_HOSTNAME=http://${DOMAIN}:38080/
EOF
fi
# nats
if [[ -f nats/overlays/prod/nats-server.env ]]; then
    echo "nats.conf already exists"
else
    cat <<EOF > nats/overlays/prod/nats-server.env
port: 4222
jetstream: enabled
jetstream {
    store_dir=/nats/storage
}
server_name=nats-server
monitor_port: 8222

authorization {  
    default_permissions = {
    publish = "SANDBOX.*"
    subscribe = ["PUBLIC.>", "_INBOX.>"]
    }

    ADMIN = {
    publish = ">"
    subscribe = ">"
    }
    
    AUTOMATION_SERVER ={
    publish = ["client.>"]
    subscribe = "_INBOX.>"
    }

    AUTOMATION_CLIENT = {
    publish = "_INBOX.>"
    subscribe = ["client.>"]
    }

    users [
    {user: "admin",   password: "${NATS_ADMIN_PASSWORD}", permissions: \$ADMIN}
    {user: "server",  password: "${NATS_SERVER_PASSWORD}", permissions: \$AUTOMATION_SERVER}
    {user: "client",  password: "${NATS_CLIENT_PASSWORD}", permissions: \$AUTOMATION_CLIENT}
    ]
}
EOF
fi

if [[ -f nats.env ]]; then
    echo "nats.env already exists"
else
    cat <<EOF > nats.env
NATS_ADMIN_PASSWORD=${NATS_ADMIN_PASSWORD}
NATS_SERVER_PASSWORD=${NATS_SERVER_PASSWORD}
NATS_CLIENT_PASSWORD=${NATS_CLIENT_PASSWORD}
EOF
fi

# system-manager
if [[ -f postgres/overlays/system-manager/postgres.env ]]; then
    echo "system-manager postgres.env already exists"
else
    cat <<EOF > postgres/overlays/system-manager/postgres.env
POSTGRES_USER=system-manager
POSTGRES_PASSWORD=${SYSTEM_MANGER_POSTGRES_PASSWORD}
EOF
fi

if [[ -f system-manager/overlays/prod/system-manager.env ]]; then
    echo "system-manager.env already exists"
else
    cat <<EOF > system-manager/overlays/prod/system-manager.env
DEBUG=True
DB_NAME=system-manager
DB_USER=system-manager
DB_HOST=postgres
DB_PASSWORD=${SYSTEM_MANGER_POSTGRES_PASSWORD}
DB_PORT=5432
SECRET_KEY=${SYSTEM_MANGER_KEYCLOAK_SECRET}
KEYCLOAK_URL_API=http://${DOMAIN}:38080/
KEYCLOAK_REALM=lite
KEYCLOAK_CLIENT_ID=lite
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
NATS_SERVERS=nats://admin:${NATS_ADMIN_PASSWORD}@nats.prod-nats.svc.cluster.local:4222
NATS_NAMESPACE=system_mgmt
CLIENT_ID=system-manager
EOF
fi

# 按顺序启动服务
kubectl create ns prod-keycloak
kubectl apply -k postgres/overlays/keycloak
kubectl apply -k keycloak/overlays/prod

kubectl create ns prod-nats
kubectl apply -k nats/overlays/prod

# 等待keycloak容器状态正常
while [[ $(kubectl get pods -n prod-keycloak | grep keycloak | awk '{print $3}') != "Running" ]]; do
    sleep 5
    echo "waiting for keycloak pod to be ready"
done

kubectl create ns prod-system-manager
kubectl apply -k postgres/overlays/system-manager
kubectl apply -k system-manager/overlays/prod

# 等待system-manager容器状态正常
while [[ $(kubectl get pods -n prod-system-manager | grep system-manager | awk '{print $3}') != "Running" ]]; do
    sleep 5
    echo "waiting for system-manager pod to be ready"
done

# 刷新lite和opspilot的token
if [[ -f keycloak_token.env ]]; then
    echo "keycloak_token.env already exists"
    source keycloak_token.env
else
    LITE_TOKEN_RAW=$(kubectl exec -i -n prod-keycloak $(kubectl get pods -n prod-keycloak -l app=keycloak -o=jsonpath='{.items[*].metadata.name}') -- /opt/keycloak/bin/refresh_token.sh lite 2>&1)
    LITE_TOKEN=$(echo $LITE_TOKEN_RAW | awk -F'"value" *: *"' '{print $2}' | awk -F'"' '{print $1}')
    OPSPILIT_TOKEN_RAW=$(kubectl exec -i -n prod-keycloak $(kubectl get pods -n prod-keycloak -l app=keycloak -o=jsonpath='{.items[*].metadata.name}') -- /opt/keycloak/bin/refresh_token.sh opspilot 2>&1)
    OPSPILIT_TOKEN=$(echo $OPSPILIT_TOKEN_RAW | awk -F'"value" *: *"' '{print $2}' | awk -F'"' '{print $1}')
    cat <<EOF > keycloak_token.env
LITE_TOKEN=${LITE_TOKEN}
OPSPILIT_TOKEN=${OPSPILIT_TOKEN}
DOMAIN=${DOMAIN}
EOF
fi

# 启动system-manager-web
if [[ -f system-manager-web/overlays/prod/system-manager-web.env ]]; then
    echo "system-manager-web.env already exists"
else
    cat <<EOF > system-manager-web/overlays/prod/system-manager-web.env
KEYCLOAK_CLIENT_ID=lite
KEYCLOAK_CLIENT_SECRET=${LITE_TOKEN}
KEYCLOAK_ISSUER=http://${DOMAIN}:38080/realms/lite
NEXTAUTH_URL=http://${DOMAIN}:38081
NEXTAUTH_SECRET=${SYSTEM_MANGER_WEB_NEXT_AUTH_SECRET}
NEXTAPI_URL=http://system-manager:8000
EOF
fi

kubectl apply -k system-manager-web/overlays/prod