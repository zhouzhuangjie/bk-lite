FROM ubuntu:24.04

ENV SERVER_URL ""
ENV SERVER_API_TOKEN ""
ENV SIDECAR_ZONE "default"
ENV SIDECAR_GROUP "default"

RUN apt-get update && \
    apt-get install -y ca-certificates ipmitool vim && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/fusion-collectors/

# Sidecar 
ADD ./collector-sidecar collector-sidecar
ADD ./sidecar.yml sidecar.yml
ADD ./startup.sh startup.sh
RUN mkdir -p /opt/fusion-collectors/bin
RUN mkdir -p /opt/fusion-collectors/cache
RUN mkdir -p /opt/fusion-collectors/log
RUN mkdir -p /opt/fusion-collectors/generated
RUN chmod +x /opt/fusion-collectors/startup.sh

# Telegraf
ADD ./mibs /usr/share/snmp/mibs
ADD ./telegraf ./bin/telegraf

# NatsExecutor
ADD ./nats-executor ./bin/nats-executor

# Vector
ADD ./vector ./bin/vector

ENTRYPOINT [ "/opt/fusion-collectors/startup.sh" ]

