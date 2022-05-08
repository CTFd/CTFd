FROM ubuntu:20.04

RUN apt-get update
RUN apt-get update && apt-get install -y build-essential socat libseccomp-dev

ARG FLAG
ARG USER
ENV USER $USER
ENV FLAG $FLAG

WORKDIR /
COPY start.sh /start.sh
RUN chmod 755 /start.sh

RUN apt-get install sudo

RUN useradd -m $USER

RUN echo "$FLAG" > /home/$USER/flag.txt
RUN chown root:root /home/$USER/flag.txt
RUN chmod 700 /home/$USER/flag.txt
RUN mkdir /libs
RUN mkdir /libs/lib32
RUN mkdir /libs/lib64
RUN mkdir /libs/lib
RUN mkdir /libs/lib64/autoconf
RUN mkdir /libs/lib64/conf
RUN mkdir /libs/lib64/sh
RUN mkdir /libs/lib64/autoconf/lib
COPY lib.sh /libs/lib64/autoconf/lib/lib.sh 



EXPOSE 9001



CMD ["/start.sh"]
