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

RUN mkdir /home/basic/flag
RUN mkdir /home/basic/right_here
RUN mkdir /home/basic/lib
RUN mkdir /home/basic/lib/flag
RUN mkdir /home/basic/lib/flag/righthere
RUN mkdir /home/basic/lib/flag/nothere
RUN mkdir /home/basic/lib/flag/oops
RUN mkdir /home/basic/hello
RUN mkdir /home/basic/hackerstuff
RUN mkdir /home/basic/maybehere
RUN mkdir /home/asdf
RUN mkdir /home/lib
RUN mkdir /home/user
RUN mkdir /home/abc
RUN mkdir /home/asdf/lib
RUN mkdir /home/asdf/flag
RUN mkdir /home/asdf/right_here
RUN mkdir /home/asdf/maybe_here
RUN mkdir /home/asdf/here
RUN mkdir /home/asdf/lib/flag
RUN mkdir /home/asdf/lib/flag/righthere
RUN mkdir /home/asdf/lib/flag/nothere
RUN mkdir /home/asdf/lib/flag/oops
RUN mkdir /home/asdf/lib/flag/hmm
RUN mkdir /home/asdf/lib/flag/maybe_here
RUN mkdir /home/asdf/lib/flag/hmm/is_it_here
RUN mkdir /libs
RUN mkdir /libs/lib32
RUN mkdir /libs/lib64
RUN mkdir /libs/lib
RUN mkdir /libs/lib64/autoconf
RUN mkdir /libs/lib64/conf
RUN mkdir /libs/lib64/sh
RUN mkdir /libs/lib64/autoconf/lib
RUN mkdir /home/user/looks_promising
RUN mkdir /home/asdf/are_you_tired
RUN mkdir /home/abc/1dont
RUN mkdir /home/abc/2do
RUN mkdir /home/abc/3this
RUN mkdir /home/abc/4manually
RUN mkdir /home/asdf/flag/find
RUN mkdir /home/asdf/flag/here

RUN echo "$FLAG" > /libs/lib64/autoconf/lib/flag.txt
RUN chown root:root /libs/lib64/autoconf/lib/flag.txt
RUN chmod 644 /libs/lib64/autoconf/lib/flag.txt



EXPOSE 9001



CMD ["/start.sh"]
