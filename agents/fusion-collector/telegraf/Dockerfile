FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y ca-certificates ipmitool vim&& \
    update-ca-certificates supervisor && \
    rm -rf /var/lib/apt/lists/*
    
ADD ./mibs /usr/share/snmp/mibs

WORKDIR /apps
ADD ./telegraf.conf ./telegraf.conf
ADD ./telegraf ./bin/telegraf
ADD ./service.conf /etc/supervisor/conf.d/service.conf

RUN chmod 777 /apps

ENTRYPOINT [ "/apps/startup.sh" ]