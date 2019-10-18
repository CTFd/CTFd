FROM alpine

RUN apk update && apk add python3 python3-dev linux-headers libffi-dev gcc \
    make musl-dev mysql-client git openssl-dev --no-cache

RUN adduser -D -s /bin/bash ctfd ctfd

WORKDIR /opt/CTFd
COPY --chown=ctfd:ctfd migrations migrations/
COPY --chown=ctfd:ctfd CTFd CTFd/
COPY --chown=ctfd:ctfd *.py *.json *.sh requirements.txt LICENSE .

RUN mkdir -p /var/log/CTFd /var/uploads
RUN chown -R ctfd:ctfd /var/log/CTFd /var/uploads

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

ENV DATABASE_URL=mysql+pymysql://root:ctfd@db/ctfd \
    REDIS_URL=redis://cache:6379 \
    UPLOAD_FOLDER=/var/uploads   \
    LOG_FOLDER=/var/log/CTFd     \
    ACCESS_LOG=-                 \
    ERROR_LOG=-                  \
    WORKERS=1

USER ctfd
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
