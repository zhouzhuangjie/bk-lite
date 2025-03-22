#!/bin/bash
source ../infra/nats.env
source ../infra/keycloak_token.env
rnd_password() {
    echo $(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
}
# 生成需要的密码环境变量
MINIO_ROOT_PASSWORD=$(rnd_password)
ELASTIC_PASSWORD=$(rnd_password)
RABBITMQ_PASSWORD=$(rnd_password)
MUNCHKIN_POSTGRES_PASSWORD=$(rnd_password)
MUNCHKIN_SECRET_KEY=$(rnd_password)
MUNCHKIN_WEB_SECRET=$(rnd_password)
KUBE_SERVICE_TOKEN=$(rnd_password)

# 生成需要的env文件
# minio
if [[ -f minio/overlays/prod/minio.env ]]; then
    echo "minio.env already exists"
else
    cat <<EOF > minio/overlays/prod/minio.env
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
EOF
fi

# elasticsearch
if [[ -f elasticsearch/overlays/prod/elasticsearch.env ]]; then
    echo "elasticsearch.env already exists"
else
    cat <<EOF > elasticsearch/overlays/prod/elasticsearch.env
ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
EOF
fi

# rabbitmq
if [[ -f rabbitmq/overlays/prod/rabbitmq.env ]]; then
    echo "rabbitmq.env already exists"
else
    cat <<EOF > rabbitmq/overlays/prod/rabbitmq.env
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
EOF
fi

# postgres
if [[ -f ../infra/postgres/overlays/munchkin/postgres.env ]]; then
    echo "postgres.env already exists"
else
    cat <<EOF > ../infra/postgres/overlays/munchkin/postgres.env
POSTGRES_USER=munchkin
POSTGRES_PASSWORD=${MUNCHKIN_POSTGRES_PASSWORD}
EOF
fi

# kube-service
if [[ -f kube-service/overlays/prod/kube-service.env ]]; then
    echo "kube-service.env already exists"
else
    cat <<EOF > kube-service/overlays/prod/kube-service.env
TOKEN=${KUBE_SERVICE_TOKEN}
EOF
fi

# munchkin
if [[ -f munchkin/overlays/prod/munchkin.env ]]; then
    echo "munchkin.env already exists"
else
    cat <<EOF > munchkin/overlays/prod/munchkin.env
DEBUG=0
DB_ENGINE=postgresql
DB_NAME=munchkin
DB_USER=munchkin
DB_PASSWORD=$MUNCHKIN_POSTGRES_PASSWORD
DB_HOST=postgres
DB_PORT=5432

SECRET_KEY=${MUNCHKIN_SECRET_KEY}

MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
MINIO_ENDPOINT=minio:9000
MINIO_EXTERNAL_ENDPOINT_USE_HTTPS=False

ELASTICSEARCH_URL=http://elasticsearch:80
ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}

CELERY_BROKER_URL=amqp://admin:${RABBITMQ_PASSWORD}@rabbitmq-service:5672
BROKER_URL=amqp://admin:${RABBITMQ_PASSWORD}@rabbitmq-service:5672

KUBE_SERVER_URL=http://kube-service
KUBE_NAMESPACE=prod-ops-pilot
KUBE_TOKEN=${KUBE_SERVICE_TOKEN}

MUNCHKIN_BASE_URL=http://opspilot:8000
CONVERSATION_MQ_HOST=rabbitmq-service
CONVERSATION_MQ_PORT=5672
CONVERSATION_MQ_USER=admin
CONVERSATION_MQ_PASSWORD=${RABBITMQ_PASSWORD}

FILE_CHUNK_SERVICE_URL=http://chunk-server/file_chunk
MANUAL_CHUNK_SERVICE_URL=http://chunk-server/manual_chunk
WEB_PAGE_CHUNK_SERVICE_URL=http://chunk-server/webpage_chunk
OPENAI_CHAT_SERVICE_URL=http://chat-server/openai
REMOTE_INDEX_URL=http://rag-server/elasticsearch_index
RAG_SERVER_URL=http://rag-server/elasticsearch_rag
ONLINE_SEARCH_SERVER_URL=http://rag-server/online_search

NATS_SERVERS=nats://admin:${NATS_ADMIN_PASSWORD}@nats.prod-nats.svc.cluster.local:4222
NATS_NAMESPACE=prod-nats
CLIENT_ID=opspilot
EOF
fi

# munchkin web
if [[ -f munchkin-web/overlays/prod/munchkin-web.env ]]; then
    echo "munchkin-web.env already exists"
else
    cat <<EOF > munchkin-web/overlays/prod/munchkin-web.env
KEYCLOAK_CLIENT_ID=lite
KEYCLOAK_CLIENT_SECRET=${LITE_TOKEN}
KEYCLOAK_ISSUER=http://${DOMAIN}:38080/realms/lite
NEXTAUTH_URL=http://${DOMAIN}:38082
NEXTAUTH_SECRET=${MUNCHKIN_WEB_SECRET}
NEXTAPI_URL="http://opspilot:8000"
NEXT_PUBLIC_USE_LOCAL_PERMISSIONS="true"
EOF
fi

kubectl create ns prod-ops-pilot
kubectl apply -k minio/overlays/prod
kubectl apply -k elasticsearch/overlays/prod
kubectl apply -k rabbitmq/overlays/prod
kubectl apply -k chat-server/overlays/prod
kubectl apply -k rag-server/overlays/prod
kubectl apply -k ocr-server/overlays/prod
kubectl apply -k chunk-server/overlays/prod
kubectl apply -k bce-embed-server/overlays/prod
kubectl apply -k fast-embed-server/overlays/prod
kubectl apply -k ../infra/postgres/overlays/munchkin
kubectl apply -k kube-service/overlays/prod
kubectl apply -k munchkin/overlays/prod
kubectl apply -k munchkin-web/overlays/prod