run-server:
	python3 server/server.py

run-client:
	python3 client/client.py

init:
	docker pull ubuntu:22.04
	kind create cluster --name demo

build:
	docker build ./client -t client
	docker build ./server -t server
	
deploy: build deploy-server deploy-client

deploy-server:
	# kind load docker-image server:latest --name demo
	kubectl apply -f server/deployment.yaml

deploy-client:
	# kind load docker-image client:latest --name demo
	kubectl apply -f client/deployment.yaml

clean:
	kubectl delete -f server/deployment.yaml
	kubectl delete -f client/deployment.yaml
