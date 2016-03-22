# Pull base image
FROM alpine:3.2

# ------------------------------------------------------------------------------
# Install Base
RUN apk update && apk upgrade
RUN apk add git gcc musl-dev libffi-dev python python-dev py-pip

# ------------------------------------------------------------------------------
# Set up CTFd
RUN mkdir /opt
WORKDIR /opt
RUN git clone https://github.com/isislab/CTFd.git
WORKDIR /opt/CTFd
RUN pip install -r requirements.txt
RUN pip install pymysql

# ------------------------------------------------------------------------------
# Configure hostname

#RUN sed -i -e "s/ctfd.io/example.com/" /opt/CTFd/CTFd/config.py

# ------------------------------------------------------------------------------
# Expose ports.
EXPOSE 8000

# ------------------------------------------------------------------------------
# Start gunicorn (defines startup command)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "CTFd:create_app()", "&"]
