FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install build-essential python-dev python-pip libffi-dev -y

VOLUME ["/opt/CTFd"]

RUN mkdir -p /opt/CTFd
COPY . /opt/CTFd
WORKDIR /opt/CTFd

RUN pip install -r requirements.txt
RUN pip install pymysql

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "CTFd:create_app()"]
EXPOSE 8000
