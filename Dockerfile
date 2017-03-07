FROM ubuntu:16.04

RUN apt update && \
    apt install -y \
        build-essential \
        libffi-dev \
        mysql-client \
        python-dev \
        python-pip && \
    rm -rf /var/lib/apt/lists/*

VOLUME ["/opt/CTFd"]

RUN mkdir -p /opt/CTFd
COPY . /opt/CTFd
WORKDIR /opt/CTFd

RUN pip install -r requirements.txt
RUN pip install pymysql

RUN chmod +x /opt/CTFd/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "CTFd:create_app()", "--access-logfile", "/opt/CTFd/CTFd/logs/access.log", "--error-logfile", "/opt/CTFd/CTFd/logs/error.log"]
