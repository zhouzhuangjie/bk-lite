FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get install -y libhdf5-dev vim  unzip curl pkg-config libssl-dev libffi-dev supervisor python3.12-dev python3.12-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/;


WORKDIR /app

ADD ./requirements/requirements-core.txt ./requirements/requirements-core.txt
ADD ./requirements/requirements-olmocr.txt ./requirements/requirements-olmocr.txt

RUN pip3 install -r ./requirements/requirements-core.txt
RUN pip3 install -r ./requirements/requirements-olmocr.txt

#ADD ./dist .

ADD ./server.py ./server.py
ADD ./core ./core
ADD ./apps/__init__.py ./apps/__init__.py
ADD ./apps/olmocr ./apps/olmocr
ADD ./modelscope /root/.cache/modelscope

ADD ./support-files/release/olmocr/service.conf /etc/supervisor/conf.d/service.conf

ENV INSTALL_APPS="olmocr"
CMD ["supervisord", "-n"]