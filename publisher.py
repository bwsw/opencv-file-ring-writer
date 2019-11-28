import cv2
import zmq
import lz4.frame
import pickle
from time import time

cap = cv2.VideoCapture(0)

context = zmq.Context()
dst = context.socket(zmq.PUB)
dst.bind("tcp://127.0.0.1:5557")

frameno = 0
COMPRESSED = True

opencv_time = 0
zmq_time = 0

while True:
    begin = time()
    ret, frame = cap.read()
    ts = time()
    opencv_time += (ts - begin) * 1000
    frameno += 1
    if COMPRESSED:
        dst.send(lz4.frame.compress(pickle.dumps(frame)))
    else:
        dst.send_pyobj(frame)
    dst.send_pyobj(dict(ts=ts, frameno=frameno))
    end = time()
    zmq_time += (end - ts) * 1000
    if frameno % 1000 == 0:
        print("OpenCV", opencv_time / frameno, "ZMQ", zmq_time / frameno)
