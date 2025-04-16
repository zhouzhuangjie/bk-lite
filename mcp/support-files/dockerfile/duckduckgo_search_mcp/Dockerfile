FROM python:3.12

RUN apt-get update && \
    apt-get install -y libhdf5-dev vim  unzip curl pkg-config libssl-dev libffi-dev supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD ./requirements/requirements-core.txt ./requirements/requirements-core.txt
ADD ./requirements/requirements-duckduckgo_search_mcp.txt ./requirements/requirements-duckduckgo_search_mcp.txt

RUN pip install -r ./requirements/requirements-core.txt
RUN pip install -r ./requirements/requirements-duckduckgo_search_mcp.txt

ADD ./apps/__init__.py ./apps/__init__.py
ADD ./apps/duckduckgo_search_mcp ./apps/duckduckgo_search_mcp

ADD ./support-files/supervisor/duckduckgo_search_mcp/mcp_server.conf /etc/supervisor/conf.d/mcp_server.conf

CMD ["supervisord", "-n"]