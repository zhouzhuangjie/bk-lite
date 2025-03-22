#!/bin/bash
kubectl delete -k minio/overlays/prod
kubectl delete -k elasticsearch/overlays/prod
kubectl delete -k rabbitmq/overlays/prod
kubectl delete -k chat-server/overlays/prod
kubectl delete -k rag-server/overlays/prod
kubectl delete -k ocr-server/overlays/prod
kubectl delete -k chunk-server/overlays/prod
kubectl delete -k bce-embed-server/overlays/prod
kubectl delete -k fast-embed-server/overlays/prod
kubectl delete -k ../infra/postgres/overlays/munchkin
kubectl delete -k kube-service/overlays/prod
kubectl delete -k munchkin/overlays/prod
kubectl delete -k munchkin-web/overlays/prod
kubectl delete ns prod-ops-pilot
rm -vf elasticsearch/overlays/prod/elasticsearch.env
rm -vf minio/overlays/prod/minio.env
rm -vf kube-service/overlays/prod/kube-service.env
rm -vf rabbitmq/overlays/prod/rabbitmq.env
rm -vf ../infra/postgres/overlays/munchkin/postgres.env
rm -vf munchkin/overlays/prod/munchkin.env
rm -vf munchkin-web/overlays/prod/munchkin-web.env