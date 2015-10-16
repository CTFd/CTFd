FROM ubuntu:trusty
RUN apt-get update && apt-get upgrade -y

RUN apt-get install git -y
RUN git clone https://github.com/isislab/CTFd.git /opt/CTFd && cd /opt/CTFd && ./prepare.sh
RUN pip install -U gunicorn

WORKDIR /opt/CTFd
CMD ["SECRET_KEY=`head -c 24 /dev/urandom` | base64 | tr -d ' \n\t\r'", "gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "CTFd:create_app()"]
EXPOSE 8000
