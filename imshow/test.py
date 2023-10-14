import cv2
import numpy as np

im = np.random.random((800, 800, 3))
cv2.imshow("img", im)
cv2.waitKey(0)