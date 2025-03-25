# -- coding: utf-8 --
# @File: collect_service.py
# @Time: 2025/2/27 11:29
# @Author: windyzhao
# -- coding: utf-8 --
# @File: collect_service.py
# @Time: 2025/2/27 11:29
# @Author: windyzhao
import traceback
import importlib
from sanic.log import logger


class CollectService(object):
    def __init__(self, params: dict):
        self.params = params
        self.plugin_name = self.params.pop("plugin_name")
        self.plugin_name_map = {
            "vmware_info": "VmwareManage",
            "snmp_facts": "SnmpFacts"
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
            return ""
