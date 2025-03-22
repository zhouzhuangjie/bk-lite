#!/bin/bash
# 按顺序启动服务
kubectl delete -k postgres/overlays/keycloak
kubectl delete -k keycloak/overlays/prod
kubectl delete ns prod-keycloak

kubectl delete -k nats/overlays/prod
kubectl delete ns prod-nats

kubectl delete -k postgres/overlays/system-manager
kubectl delete -k system-manager/overlays/prod
kubectl delete ns prod-system-manager

rm -vf keycloak/overlays/prod/keycloak.env
rm -vf postgres/overlays/system-manager/postgres.env
rm -vf postgres/overlays/keycloak/postgres.env
rm -vf system-manager/overlays/prod/system-manager.env
rm -vf nats/overlays/prod/nats-server.env
rm -vf nats.env
rm -vf keycloak_token.env
rm -vf system-manager-web/overlays/prod/system-manager-web.env