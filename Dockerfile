FROM alpine:3.2
RUN apk update && apk upgrade
RUN apk add git gcc musl-dev libffi-dev python python-dev py-pip

RUN mkdir /opt
COPY . /opt/CTFd
WORKDIR /opt/CTFd

RUN pip install -r requirements.txt
RUN pip install pymysql

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "CTFd:create_app()"]
EXPOSE 8000
