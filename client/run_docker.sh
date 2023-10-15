ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
docker run --rm -it -e DISPLAY=$ip:0  --net=aiortc --name aiortc_client aiortc_client bash
# python3.11 client.py --host aiortc_server.aiortc