# 使用compose部署bk-lite

#### TL;DR

部署前提：docker >= 20.10.23, docker-compose >=v2.27.0 

```bash
#!/bin/bash
# 将此仓库克隆到本地目录
cd deploy/docker-compose
# 启动服务,一直回车即可,有调整端口需求见下文
bash bootstrap.sh
# bootstrap.sh是幂等的，多次运行不会对当前部署造成影响
```

#### 端口映射说明

| 端口号 | 用途                                |
| ------ | ----------------------------------- |
| 20000  | keycloak访问端口，用于登录鉴权      |
| 20001  | 系统管理访问端口                    |
| 20002  | 节点管理访问端口                    |
| 20003  | 监控页面访问端口                    |
| 20004  | 控制台页面访问端口                  |
| 20005  | 节点管理API端口，用于外部控制器通讯 |

#### 如何干净卸载

> 需在deploy/compose目录下执行

```bash
#!/bin/bash
# 清除现有的容器，卷和网络
docker-compose --profile lite down --volumes
# 清除生成的安装包，环境变量和compose文件
rm -rvf pkgs *.env docker-compose.yml
```

