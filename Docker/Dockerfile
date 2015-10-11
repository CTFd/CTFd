FROM ubuntu:trusty

RUN apt-get clean && apt-get update && apt-get upgrade -y

RUN apt-get install git nginx python-pip python-dev build-essential libffi-dev -y
RUN pip install uwsgi;
RUN useradd -m ctfduser

VOLUME [ "/opt/ctfd" ]
EXPOSE 8000
ADD ctfd /usr/local/bin/ctfd
RUN chmod +x /usr/local/bin/ctfd
ENTRYPOINT [ "/usr/local/bin/ctfd"  ]
