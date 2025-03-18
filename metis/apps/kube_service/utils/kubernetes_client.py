import os

from kubernetes import client, config


class KubernetesClient:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        if os.getenv('KUBE_CONFIG_FILE') == "":
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file=os.getenv('KUBE_CONFIG_FILE'))

        self.core_api = client.CoreV1Api()
        self.app_api = client.AppsV1Api()
        self.storage_api = client.StorageV1Api()
        self.custom_object_api = client.CustomObjectsApi()
        self.batch_api = client.BatchV1Api()
        self.traefik_resource_group = "traefik.containo.us"

        self.argo_resource_group = "argoproj.io"
        self.argo_resource_version = "v1alpha1"
