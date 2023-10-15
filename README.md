# Nimble Programming Challenge

## Install & Run

The followings are two approaches to setup the run-time to execute this the demo of bouncing ball.

### Kubernetes with Docker
- Install [`Docker`](https://docs.docker.com/get-docker/), [`Kubectl`](https://kubernetes.io/docs/tasks/tools/) according to their official guidelines.
- Follow the instructions to create X11 depending on your OS
    - Ubuntu
    ```
    TBD
    ```
    - Mac OSX (tested in Ventura 13.5.1 (22G90))
    ```bash
    open -a Xquartz # You should see a Xquartz pop out in your Mac docker
    Go to Xquartz > Settings > Security > Check "Allow connections from network clients"
    Right click on Xquartz > Application > Terminal # You should see a `xterm` window pop out

    # In xterm, run the following
    ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
    xhost $ip
    
    # Swtich back to normal terminal, run the following
    source set_x11_macosx.sh
    ```
- Initialize `minikube`
    ```bash
    minikube start
    minikube docker-env
    ```
- Build docker images and launch Kubernete cluster
    ```
    make deploy
    ```
- You should see server and client windows and ball bouncing in the windows.

### Conda
- Install [`miniconda`](https://docs.conda.io/projects/miniconda/en/latest/) or [`anaconda`](https://docs.anaconda.com/free/anaconda/install/index.html)
- Create conda environment from the dependencies file
    ```
    conda env create -n nimble -f environment.yml
    ```
- Activate the conda environment
    ```
    conda activate nimble
    ```
- Sepearately run `python3 server.py` and `python3 client.py`
    ```
    python3 server/server.py
    python3 client/client.py
    ```


## Test
The test scripts are `server/test_server.py` and `client/test_client.py`. You can separately run them by
```
pytest server/test_server.py
pytest client/test_client.py
```
or using `Makefile`
```bash
make test
```