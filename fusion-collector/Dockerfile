FROM telegraf:1.33.3

# 添加构建参数
ARG VERSION=latest
ARG BUILD_DATE
ARG VCS_REF
ARG ARCH=linux-arm64

# 添加镜像标签
LABEL org.label-schema.version="${VERSION}" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.name="fusion-collectors" \
      org.label-schema.schema-version="1.0"

WORKDIR /opt/fusion-collectors

RUN apt-get update && \
    apt-get install -y ca-certificates ipmitool vim&& \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*
    
ADD ./${ARCH}/bin bin
ADD ./${ARCH}/cache cache
ADD ./${ARCH}/generated generated
ADD ./${ARCH}/log log
ADD ./${ARCH}/collector-sidecar collector-sidecar
ADD ./scripts scripts
ADD ./startup.sh startup.sh

ADD ./support-files/mibs /usr/share/snmp/mibs

RUN chmod -Rf 777 /opt/fusion-collectors

ENTRYPOINT [ "/opt/fusion-collectors/startup.sh" ]