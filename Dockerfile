FROM python:3.11-slim-bookworm AS build

WORKDIR /opt/CTFd

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Install CTFd requirements before copying the whole project,
# this layer will be reused when rebuilding CTFd after a small change
COPY ./requirements.txt /opt/CTFd
RUN pip install --no-cache-dir -r requirements.txt

# Install CTFd plugins requirements
COPY . /opt/CTFd
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install --no-cache-dir -r "$d/requirements.txt";\
        fi; \
    done;


FROM python:3.11-slim-bookworm AS release
WORKDIR /opt/CTFd

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
