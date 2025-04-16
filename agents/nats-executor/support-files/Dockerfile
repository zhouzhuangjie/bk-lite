FROM ubuntu:24.04

ENV NATS_INSTANCE_ID "default"
ENV NATS_URLS "nats://admin:password@nats:4222"

ADD ./nats-executor /opt/nats-executor
ADD ./support-files/startup.sh /opt/startup.sh
RUN chmod +x /opt/startup.sh
RUN chmod +x /opt/nats-executor

ENTRYPOINT [ "/opt/startup.sh" ]
