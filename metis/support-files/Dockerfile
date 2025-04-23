FROM python:3.12

RUN apt-get update && \
    apt-get install -y libhdf5-dev vim  unzip curl pkg-config libssl-dev libffi-dev supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . .

RUN pip install -r ./requirements/requirements.in
RUN pip install -r ./requirements/requirements-dev.in
RUN playwright install chromium
ADD ./support-files/service.conf /etc/supervisor/conf.d/service.conf

ENTRYPOINT ["/bin/bash","/apps/support-files/startup.sh"]