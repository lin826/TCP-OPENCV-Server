test:
	pytest server/test_server.py
	pytest client/test_client.py

init:
	docker pull ubuntu:22.04

build:
	docker build ./client -t client
	docker build ./server -t server
	
deploy: build deploy-server deploy-client

deploy-server:
	DISPLAY=${XSERVER_IP}:0 envsubst < server/deployment.yaml | kubectl apply -f -
	sleep 10

deploy-client:	
	DISPLAY=${XSERVER_IP}:0 envsubst < client/deployment.yaml | kubectl apply -f -

clean:
	kubectl delete -f server/deployment.yaml
	kubectl delete -f client/deployment.yaml

debug: build
	kubectl delete -f client/deployment.yaml
	kubectl apply -f client/deployment.yaml
