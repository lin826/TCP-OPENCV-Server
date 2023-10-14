Run `cv2.imshow` in docker (in Mac OSX 13.5.1 (22G90))
=

Steps
==
1. Create a container and connect its display to the host
```
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
docker run -it -e DISPLAY=$ip:0 {image_name}
```
2. Create a X11 server
```
open -a Xquartz # You should see a Xquartz pop out in your Mac docker
Go to Xquartz > Settings > Security > Check "Allow connections from network clients"
Right click on Xquartz > Application > Terminal # You should see a `xterm` window pop out

ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost $ip
```

3. Go to the container created at Step 1 and try GUI apps
```
xeyes
```
You should see an `xeyes` window shown on your desktop.
```
python test.py
```
You should see a noisy image shonw in OpenCV window.

Reference
== 
[https://www.youtube.com/watch?v=cNDR6Z24KLM&ab_channel=TechHara](https://www.youtube.com/watch?v=cNDR6Z24KLM&ab_channel=TechHara)