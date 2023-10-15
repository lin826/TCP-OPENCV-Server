test:
	pytest .

init:
	docker pull ubuntu:22.04

build:
	docker build ./client -t client
	docker build ./server -t server
	
deploy: build deploy-server deploy-client

deploy-server:
	kubectl apply -f server/deployment.yaml
	sleep 10

deploy-client:
	kubectl apply -f client/deployment.yaml

clean:
	kubectl delete -f server/deployment.yaml
	kubectl delete -f client/deployment.yaml

debug: build
	kubectl delete -f client/deployment.yaml
	kubectl apply -f client/deployment.yaml
