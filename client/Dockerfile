FROM ubuntu:22.04

WORKDIR /usr/
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

RUN apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx

RUN apt-get update
RUN apt-get install x11-apps -y
RUN apt-get install iputils-ping -ys
RUN apt-get install vim -y

#install aiortc and other python libs
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./ ./
CMD python3 ./client.py --host server --port 8080
EXPOSE 8080
