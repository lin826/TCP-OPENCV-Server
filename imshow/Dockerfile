FROM ubuntu:22.04

RUN apt-get update

#install aiortc dependencies
RUN apt-get install -y \
    python3-pip \
    libglib2.0-0 \
    libgl1-mesa-glx

RUN apt-get update
RUN apt-get install x11-apps -y

RUN pip install opencv-python

COPY ./test.py /test.py
