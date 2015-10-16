FROM ubuntu:trusty
RUN apt-get update && apt-get upgrade -y

RUN apt-get install git -y
RUN git clone https://github.com/isislab/CTFd.git /opt/CTFd && cd /opt/CTFd && ./prepare.sh
RUN pip install -U gunicorn

WORKDIR /opt/CTFd
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "--env", "SECRET_KEY=`head -c 64 /dev/urandom`", "CTFd:create_app()"]
EXPOSE 8000
