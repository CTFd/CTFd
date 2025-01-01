FROM python:3.12-alpine

COPY ./notification.requirements.txt /requirements.txt
RUN pip install --no-cache -r /requirements.txt

COPY ./crontab.txt /etc/crontabs/root

WORKDIR /opt/notification

COPY ./src .

CMD [ "crond", "-f", "&&", "tail", "-f", "/dev/null" ]