FROM python:3.12

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/;
RUN rm -Rf /etc/apt/sources.list.d \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list;

RUN apt-get update && \
    apt-get install -y libhdf5-dev vim  unzip curl pkg-config libssl-dev libffi-dev supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD ./requirements/requirements-core.txt ./requirements/requirements-core.txt
ADD ./requirements/requirements-rag_service.txt ./requirements/requirements-rag_service.txt

RUN pip install -r ./requirements/requirements-core.txt
RUN pip install -r ./requirements/requirements-rag_service.txt

#ADD ./dist .

ADD ./server.py ./server.py
ADD ./core ./core
ADD ./apps/__init__.py ./apps/__init__.py
ADD ./apps/rag_service ./apps/rag_service

ADD ./support-files/release/rag_service/service.conf /etc/supervisor/conf.d/service.conf

ENV INSTALL_APPS="rag_service"
CMD ["supervisord", "-n"]