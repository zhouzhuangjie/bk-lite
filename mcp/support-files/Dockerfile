FROM python:3.12

ARG MCP_APP

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

ADD ../requirements/requirements-core.txt ./requirements/requirements-core.txt
ADD ./requirements/requirements-${MCP_APP}.txt ./requirements/requirements-${MCP_APP}.txt

RUN pip install -r ./requirements/requirements-core.txt
RUN pip install -r ./requirements/requirements-${MCP_APP}.txt


ADD ./${MCP_APP} ./${MCP_APP}

ADD ./support-files/release/chat_service/service.conf /etc/supervisor/conf.d/service.conf

ADD ./support-files/release/chat_service/general_mcp.conf /etc/supervisor/conf.d/general_mcp.conf

ADD ./support-files/release/chat_service/web_search_mcp.conf /etc/supervisor/conf.d/web_search_mcp.conf

CMD python ./${MCP_APP}/server.py
