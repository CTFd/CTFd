FROM python:3.11-slim-bookworm AS build

WORKDIR /opt/CTFd

# hadolint ignore=DL3008
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

COPY . /opt/CTFd

RUN pip install --no-cache-dir -r requirements.txt \
    && for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install --no-cache-dir -r "$d/requirements.txt";\
        fi; \
    done;


FROM python:3.11-slim-bookworm AS release
WORKDIR /opt/CTFd

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libffi8 \
        libssl3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --no-log-init --shell /bin/bash -u 1001 ctfd \
    && mkdir -p /var/log/CTFd /var/uploads /opt/CTFd \
    && chown -R ctfd:ctfd /var/log/CTFd /var/uploads /opt/CTFd

COPY --chown=ctfd:ctfd . /opt/CTFd
COPY --chown=ctfd:ctfd --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER ctfd
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
