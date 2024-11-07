FROM python:3.11-slim-bookworm
WORKDIR /opt/CTFd

# Install CTFd requirements
COPY ./requirements.txt /opt/CTFd
RUN pip install --no-cache-dir -r requirements.txt

# Install CTFd plugins requirements
COPY ./CTFd/plugins/ /opt/CTFd/CTFd/plugins
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install --no-cache-dir -r "$d/requirements.txt";\
        fi; \
    done;

COPY --chown=1001:1001 . /opt/CTFd

RUN useradd \
    --no-log-init \
    --shell /bin/bash \
    -u 1001 \
    ctfd \
    && mkdir -p /var/log/CTFd /var/uploads \
    && chown -R 1001:1001 /var/log/CTFd /var/uploads /opt/CTFd \
    && chmod +x /opt/CTFd/docker-entrypoint.sh

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
