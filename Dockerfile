FROM python:3.7-alpine as base 

WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

RUN apk update && \
    apk add --no-cache \
        python \
        python-dev \
        linux-headers \
        libffi-dev \
        gcc \
        make \
        musl-dev \
        py-pip \
        mysql-client \
        git \
        openssl-dev

COPY requirements.txt /opt/CTFd
RUN pip install --user -r requirements.txt --no-cache-dir
COPY CTFd/plugins/ /opt/CTFd/CTFd/plugins/
RUN for d in CTFd/plugins/*; do \
        if [ -f "$d/requirements.txt" ]; then \
            pip install --user -r $d/requirements.txt --no-cache-dir; \
        fi; \
    done;

FROM python:3.7-alpine

WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads
COPY . /opt/CTFd

RUN chmod +x /opt/CTFd/docker-entrypoint.sh
RUN adduser -D -u 1001 -s /bin/sh ctfd
COPY --from=base /root/.local /home/ctfd/.local
ENV PATH=/home/ctfd/.local/bin:$PATH
RUN chown -R 1001:1001 /opt/CTFd /var/log/CTFd /var/uploads /home/ctfd/.local

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
