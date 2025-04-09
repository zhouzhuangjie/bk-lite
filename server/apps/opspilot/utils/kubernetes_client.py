from django.conf import settings
from langserve import RemoteRunnable

from apps.core.logger import logger
from apps.opspilot.models import Bot


class KubernetesClient:
    def __init__(self):
        """
        :param namespace: 操作的目标NameSpace
        :param kube_config_file: 目标KubeConfig，不填写则获取默认配置文件路径
        """

        self.kube_remote_url = settings.KUBE_SERVER_URL
        # self.kube_remote_url = "http://10.10.40.190:8001"
        self.headers = {"x-token": settings.KUBE_TOKEN}

    def start_pilot(self, bot: Bot):
        logger.info(f"启动Pilot: {bot.id}")

        server_runnable = RemoteRunnable(self.kube_remote_url + "/start_pilot", headers=self.headers)
        kwargs = {
            "pilot_id": bot.id,
            "api_key": bot.api_token,
            "replicas": bot.replica_count,
            "munchkin_url": settings.MUNCHKIN_BASE_URL,
            "rabbitmq_host": settings.CONVERSATION_MQ_HOST,
            "rabbitmq_port": settings.CONVERSATION_MQ_PORT,
            "rabbitmq_user": settings.CONVERSATION_MQ_USER,
            "rabbitmq_password": settings.CONVERSATION_MQ_PASSWORD,
            "enable_bot_domain": bot.enable_bot_domain,
            "enable_ssl": bot.enable_ssl,
            "bot_domain": bot.bot_domain or "",
            "enable_node_port": bot.enable_node_port,
            "node_port": bot.node_port,
            "namespace": settings.KUBE_NAMESPACE or "",
        }
        logger.info(f"pilot 参数: {kwargs}")
        try:
            result = server_runnable.invoke(kwargs)
        except Exception as e:
            logger.exception(f"启动Pilot失败: {e}")
            raise Exception("无法连接到Pilot服务，请检查服务是否正常运行。")
        return result

    def stop_pilot(self, bot_id):
        server_runnable = RemoteRunnable(self.kube_remote_url + "/stop_pilot", headers=self.headers)
        kwargs = {
            "bot_id": bot_id,
            "namespace": settings.KUBE_NAMESPACE,
        }
        result = server_runnable.invoke(kwargs)
        return result

    def list_pilot(self):
        server_runnable = RemoteRunnable(self.kube_remote_url + "/list_pilot", headers=self.headers)
        kwargs = {"namespace": settings.KUBE_NAMESPACE, "label_selector": ""}
        result = server_runnable.invoke(kwargs)
        return result
