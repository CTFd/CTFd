FROM python:3.7-slim-buster AS cache

COPY . /opt/CTFd
RUN find /opt/CTFd -name requirements.txt -exec cat {} \; > /opt/requirements.txt

FROM python:3.7-slim-buster
WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cache /opt/requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt --no-cache-dir

COPY . /opt/CTFd

RUN adduser \
    --disabled-login \
    -u 1001 \
    --gecos "" \
    --shell /bin/bash \
    ctfd
RUN chmod +x /opt/CTFd/docker-entrypoint.sh \
    && chown -R 1001:1001 /opt/CTFd /var/log/CTFd /var/uploads

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
