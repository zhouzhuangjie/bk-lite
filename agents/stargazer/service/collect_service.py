# -- coding: utf-8 --
# @File: collect_service.py
# @Time: 2025/2/27 11:29
# @Author: windyzhao
# -- coding: utf-8 --
# @File: collect_service.py
# @Time: 2025/2/27 11:29
# @Author: windyzhao
import time
import traceback
import importlib
from sanic.log import logger


class CollectService(object):
    def __init__(self, params: dict):
        self.params = params
        self.plugin_name = self.params.pop("plugin_name")
        self.plugin_name_map = {
            "vmware_info": "VmwareManage",
            "snmp_facts": "SnmpFacts",
            "snmp_topo": "SnmpTopoClient",
        }

    def collect(self):
        try:
            # 动态加载插件
            module = importlib.import_module(f'plugins.{self.plugin_name}')
            plugin_class = getattr(module, self.plugin_name_map[self.plugin_name])
            plugin_instance = plugin_class(self.params)
            result = plugin_instance.list_all_resources()
            return result
        except Exception as e:
            logger.info(f"Error loading plugin {self.plugin_name}: {traceback.format_exc()}")
            # 生成错误指标数据，直接转换为Prometheus文本格式
            current_timestamp = int(time.time() * 1000)  # 毫秒时间戳
            error_type = str(type(e).__name__)

            # 直接构造Prometheus格式字符串
            prometheus_lines = ["# HELP collection_status Auto-generated help for collection_status",
                                "# TYPE collection_status gauge"]
            # 添加采集状态指标
            status_metric = f'collection_status{{plugin="{self.plugin_name}",status="error",error_type="{error_type}"}} 1 {current_timestamp}'
            prometheus_lines.append(status_metric)

            # 确保最后以换行符结尾
            return "\n".join(prometheus_lines) + "\n"
