FROM python:2.7-alpine
RUN apk update && \
    apk add python python-dev libffi-dev gcc make musl-dev py-pip mysql-client git openssl-dev

WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /opt/CTFd

VOLUME ["/opt/CTFd"]

RUN for d in CTFd/plugins/*; do \
      if [ -f "$d/requirements.txt" ]; then \
        pip install -r $d/requirements.txt; \
      fi; \
    done;

RUN chmod +x /opt/CTFd/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
