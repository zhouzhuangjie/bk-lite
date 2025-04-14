#!/bin/bash

# 确保脚本以 root 权限运行
if [ "$(id -u)" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

echo "开始安装 Fusion Collector Sidecar 服务..."

# 复制服务文件到 systemd 目录
cp -Rf "./sidecar.service" /etc/systemd/system/

# 重新加载 systemd 配置
systemctl daemon-reload

systemctl enable --now sidecar.service
echo "服务已设置为开机自启动"

echo "安装完成"
exit 0
