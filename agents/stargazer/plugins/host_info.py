# -- coding: utf-8 --
# @File: host_info.py
# @Time: 2025/5/6 17:48
# @Author: windyzhao
# !/usr/bin/python
# -*- coding: utf-8 -*-
import json

from core.nast_request import NATSClient
from plugins.base_utils import convert_to_prometheus_format
from sanic.log import logger


class HostInfo:
    """Class for collecting host information."""

    def __init__(self, params: dict):
        self.node_id = params["node_id"]
        self.username = params.get("username")
        self.password = params.get("password")
        self.time_out = int(params.get("execute_timeout", 60))
        self.command = params.get("command", self.script)
        self.nats_client = NATSClient()

    @property
    def script(self) -> str:
        """
        采集脚本
        权限要求
            SSH访问权限:
            需要有SSH登录目标主机的权限
            建议创建一个专用的只读账号用于信息采集
            命令执行权限:
            需要执行以下命令的权限:
            uname
            cat /etc/os-release
            lscpu
            free
            df
            ip 或 ifconfig
            文件读取权限:
            需要读取 /etc/os-release 文件的权限
            需要读取 /proc/cpuinfo 和 /proc/meminfo 的权限 (通过命令间接访问)
        """
        result = """
#!/bin/bash
# 更健壮的采集脚本
set -e  # 遇到错误立即退出

# 定义fallback函数
unknown_or() {
    "$@" 2>/dev/null || echo "unknown"
}

# 操作系统信息
os_type=$(unknown_or uname -o)
os_version=$( (unknown_or grep 'PRETTY_NAME=' /etc/os-release || unknown_or grep 'VERSION=' /etc/os-release) | head -n1 | cut -d '"' -f 2)
architecture=$(unknown_or uname -m)
hostname=$(unknown_or hostname -f || unknown_or hostname)

# CPU信息
if unknown_or which lscpu >/dev/null; then
    cpu_model=$(unknown_or lscpu | grep -i 'model name' | awk -F: '{print $2}' | xargs)
    cpu_cores=$(unknown_or lscpu | grep -i '^CPU(s):' | awk -F: '{print $2}' | xargs)
else
    cpu_model=$(unknown_or grep -m1 -i 'model name' /proc/cpuinfo | awk -F: '{print $2}' | xargs)
    cpu_cores=$(unknown_or grep -c '^processor' /proc/cpuinfo)
fi

# 内存信息
if unknown_or which free >/dev/null; then
    mem_total=$(unknown_or free -m | awk '/Mem:/{print $2}')
else
    mem_total=$(unknown_or awk '/MemTotal/{printf "%.0f", $2/1024}' /proc/meminfo)
fi

# 磁盘信息
if unknown_or which df >/dev/null; then
    disk_total=$(unknown_or df -h --total 2>/dev/null | awk '/total/{print $2}' || unknown_or df -h | awk '{total+=$2}END{print total "G"}')
else
    disk_total="unknown"
fi

# 网络信息
mac_address=$( (unknown_or ip link show || unknown_or ifconfig -a) 2>/dev/null | awk '/ether/{print $2; exit}' || echo "unknown")

# 系统运行时间和负载
uptime=$(unknown_or uptime -p || unknown_or uptime | sed -n 's/^.*up *//p')
load_avg=$(unknown_or uptime | awk -F'load average: ' '{print $2}' || echo "unknown")

# 输出JSON结果
cat <<EOF
{
    "os_type": "$os_type",
    "os_version": "$os_version",
    "architecture": "$architecture",
    "cpu_model": "$cpu_model",
    "cpu_cores": "$cpu_cores",
    "mem_total": "${mem_total}MB",
    "disk_total": "$disk_total",
    "mac_address": "$mac_address",
    "hostname": "$hostname",
    "uptime": "$uptime",
    "load_avg": "$load_avg"
}
EOF
    """
        return result

    async def connect_nats(self):
        """异步连接 NATS"""
        await self.nats_client.connect()

    async def close_nats(self):
        """异步关闭 NATS"""
        await self.nats_client.close()

    @property
    def nast_id(self):
        """
        生成NATS ID
        :return:
        """
        return "ssh.execute" if self.username else "local.execute"

    def format_params(self):
        """
        格式化参数
        :return:
        """
        script_params = {
            "command": self.command,
        }
        if self.username:
            script_params["username"] = self.username
            script_params["password"] = self.password
        if self.time_out:
            script_params["execute_timeout"] = self.time_out
        return script_params

    async def exec_script(self):
        """
        调用 NATS 执行脚本
        """
        exec_params = {
            "args": [self.format_params()],
            "kwargs": {}
        }
        subject = f"{self.nast_id}.{self.node_id}"
        response = await self.nats_client.request(subject=subject, params=exec_params)  # 使用 await 调用异步方法
        return json.loads(response["result"])

    async def list_all_resources(self):
        """
        Convert collected data to a standard format.
        """
        try:
            await self.connect_nats()  # 异步连接 NATS
            data = await self.exec_script()  # 使用 await 获取执行结果
            prometheus_data = convert_to_prometheus_format({"host": [data]})
            return prometheus_data
        except Exception as err:
            import traceback
            logger.error(f"host_info main error! {traceback.format_exc()}")
        finally:
            await self.close_nats()  # 异步关闭 NATS
