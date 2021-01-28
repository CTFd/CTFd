FROM python:3.7-slim-buster AS cache

COPY . /opt/CTFd
RUN find /opt/CTFd -not -name "requirements.txt" -type f -delete

FROM python:3.7-slim-buster AS builder

COPY --from=cache /opt/CTFd /opt/CTFd
WORKDIR /opt/CTFd

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libffi-dev \
        libssl-dev \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# hadolint ignore=SC1091
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -r requirements.txt --no-cache-dir && \
    for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install -r "$d/requirements.txt" --no-cache-dir; \
        fi; \
    done;

FROM python:3.7-slim-buster
WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

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
ENTRYPOINT ["bash", "-c", "source /opt/venv/bin/activate && /opt/CTFd/docker-entrypoint.sh"]
