FROM python:3.7-slim-buster AS cache

COPY . /opt/CTFd
RUN find /opt/CTFd -not -name "requirements.txt" -type f -delete

FROM python:3.7-slim-buster
WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cache /opt/CTFd /opt/CTFd

RUN pip install -r requirements.txt --no-cache-dir

# hadolint ignore=SC2086
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install -r $d/requirements.txt --no-cache-dir; \
        fi; \
    done;

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
