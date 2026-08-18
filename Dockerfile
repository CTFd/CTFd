FROM busybox AS plugin-reqs
COPY CTFd/plugins/ /tmp/all-plugins/
RUN mkdir -p /tmp/plugins && \
    for d in /tmp/all-plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            mkdir -p "/tmp/plugins/$(basename "$d")" && \
            cp "$d/requirements.txt" "/tmp/plugins/$(basename "$d")/"; \
        fi; \
    done

FROM python:3.11-slim-bookworm AS build
WORKDIR /opt/CTFd

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /opt/CTFd/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=plugin-reqs /tmp/plugins/ /tmp/plugins/
RUN for d in /tmp/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install --no-cache-dir -r "$d/requirements.txt"; \
        fi; \
    done

FROM python:3.11-slim-bookworm AS release
WORKDIR /opt/CTFd

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libffi8 \
        libssl3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=1001:1001 . /opt/CTFd

RUN useradd \
    --no-log-init \
    --shell /bin/bash \
    -u 1001 \
    ctfd \
    && mkdir -p /var/log/CTFd /var/uploads \
    && chown -R 1001:1001 /var/log/CTFd /var/uploads /opt/CTFd \
    && chmod +x /opt/CTFd/docker-entrypoint.sh

COPY --chown=1001:1001 --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
