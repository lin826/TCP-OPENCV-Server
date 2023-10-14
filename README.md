# TCP OpenCV Server

Multiprocess to generate 2D image frames.

## Install, Run, and Test

### Kubernetes in Docker

In order to avoid execution errors on various platforms or OS, we wrap the simulation into Dockerfile.

Install [`Docker`](https://docs.docker.com/get-docker/), [`kubectl`](https://kubernetes.io/docs/tasks/tools/), [`kind`](https://kind.sigs.k8s.io/docs/user/quick-start/) according to their official guidelines.

```sh
docker pull
kubectl apply -f aiortc-deployment.yaml
```

### Local Terminals

Install [`aiortc`](https://github.com/aiortc/aiortc/tree/main#installing), [`pytuntap`](https://pypi.org/project/python-pytuntap/).

```sh
pip install -r ./requirements.txt
```

Open two seperated terminal windows, then run `python3 server.py` and `python3 client.py` respectively.

<!-- ## Develop Guide

```sh
docker build . -t <IMAGE_NAME>
docker run --cap-add=NET_ADMIN --device=/dev/net/tun <IMAGE_NAME>
``` -->

## Test

```sh
pytest test_SCRIPT.py
```

## Reference

- [Webcam server](https://github.com/aiortc/aiortc/tree/main/examples/webcam)
- [Client.py not receiving video frames from server.py #624](https://github.com/aiortc/aiortc/discussions/624)
- [Python WebRTC basics with aiortc](https://dev.to/whitphx/python-webrtc-basics-with-aiortc-48id)
- [brandenkretschmer/AIORTC_Ball_Tracking](https://github.com/brandenkretschmer/AIORTC_Ball_Tracking)
