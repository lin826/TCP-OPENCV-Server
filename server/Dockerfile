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
RUN apt-get install -y python3-pip

#install aiortc and other python libs
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./ ./
CMD python3 ./server.py
EXPOSE 8080
