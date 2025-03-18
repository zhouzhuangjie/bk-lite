# BK-Lite


## Lite-Web

BK-Lite Web应用

## Lite-Server

BK-Lite 服务端应用

## Fusion Collector

混合采集器

## Nats Executor

远端任务执行器


## Stargazer

Stargazer是一个基于Sanic，暴露Exporter数据采集服务，提供网络设备拓扑、VMWare、腾讯云等采集服务


## Infra

BK Lite的基础服务组件与部署文件

## Metis

Metis 是以LangServe为核心服务构建的服务应用，包含以下服务模块:

| 名称          | 描述                                                                |
| ------------- | ------------------------------------------------------------------- |
| paddleocr     | 为AI模块提供图片OCR识别的能力，用于图片问答、文档图片识别并提取内容 |
| olmocr        | 为AI模块提供图片OCR识别的能力，用于图片问答、文档图片识别并提取内容 |
| chat-service  | 屏蔽智能体之间的API差异，提供与智能体进行对话、Function Call的能力  |
| rag-service   | 为智能体提供RAG增强的服务                                           |
| chunk-service | 为AI模块提供文本分块服务                                            |
| kube-service  | Kubernetes的基础查询、启动Pilot的服务                               |