FROM python:2.7-alpine
RUN apk update && \
    apk add python python-dev libffi-dev gcc make musl-dev py-pip mysql-client

RUN mkdir -p /opt/CTFd
WORKDIR /opt/CTFd
COPY requirements.txt /opt/CTFd/
RUN pip install -r requirements.txt
RUN mkdir /opt/CTFd/CTFd
COPY ./CTFd/plugins/ /opt/CTFd/CTFd/plugins/
RUN for d in CTFd/plugins/*; do \
      if [ -f "$d/requirements.txt" ]; then \
        pip install -r $d/requirements.txt; \
      fi; \
    done;
COPY ./migrations/ /opt/CTFd/migrations/
COPY ./CTFd/ /opt/CTFd/CTFd/
COPY docker-entrypoint.sh /opt/CTFd/
VOLUME ["/opt/CTFd/CTFd"]
RUN chmod +x /opt/CTFd/docker-entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
