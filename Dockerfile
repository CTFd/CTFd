FROM python:3.7-alpine
WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

RUN apk update && \
    apk add --no-cache \
        python3 \
        python3-dev \
        linux-headers \
        libffi-dev \
        gcc \
        make \
        musl-dev \
        py-pip \
        mysql-client \
        git \
        openssl-dev

COPY . /opt/CTFd

RUN pip install -r requirements.txt --no-cache-dir
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install -r $d/requirements.txt --no-cache-dir; \
        fi; \
    done;

RUN chmod +x /opt/CTFd/docker-entrypoint.sh
RUN adduser -D -u 1001 -s /bin/sh ctfd
RUN chown -R 1001:1001 /opt/CTFd /var/log/CTFd /var/uploads

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
