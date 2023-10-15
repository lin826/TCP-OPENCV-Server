FROM ubuntu:22.04

RUN apt-get update

#install aiortc dependencies
RUN apt-get install -y \
    libavdevice-dev \
    libavfilter-dev \
    libopus-dev \
    libvpx-dev \
    libsrtp2-dev \
    pkg-config

RUN apt-get install -y curl python3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
# RUN apt-get install -y python3-pip

RUN apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx

RUN apt-get update
RUN apt-get install x11-apps -y
RUN apt-get install iputils-ping -y

#install aiortc and other python libs
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

RUN apt-get install vim -y
COPY ./ ./
# CMD python3 ./server.py
EXPOSE 8080
