import argparse
import asyncio
import ctypes
import json
import logging
import cv2
import numpy as np

"""
HACK: It's necessary to run cv2.imshow once before importing VideoFrame and aiortc when deploying on dockers
"""
cv2.imshow("client", np.zeros((50, 50, 3)))

import aiortc
import multiprocessing
import threading
from av import VideoFrame
from aiortc.contrib.signaling import BYE, TcpSocketSignaling

# CV_DP: Inverse ratio of the accumulator resolution to the image resolution.
CV_DP = 5
# CV_MINDIST: Minimum distance between the centers of the detected circles.
CV_MINDIST = 10

logger = logging.Logger("ping")

def process_a(frame_queue, ball_x, ball_y, timestamp):
    x_diff, y_diff = 0, 0
    while True:
        (t, frame) = frame_queue.get()
        if frame is None:
            continue
        # Process the frame with OpenCV to locate the ball and update ball_location
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(frame, cv2.HOUGH_GRADIENT, dp=CV_DP, minDist=CV_MINDIST)

        with timestamp.get_lock() and ball_x.get_lock() and ball_y.get_lock():
            if circles is not None:
                x_diff = circles[0][0][0] - ball_x.value
                y_diff = circles[0][0][1] - ball_y.value
            timestamp.value = t
            ball_x.value += int(x_diff)
            ball_y.value += int(y_diff)


async def consume_signaling(
        pc: aiortc.RTCPeerConnection, 
        signaling: TcpSocketSignaling,
) -> bool:
    obj = await signaling.receive()
    if obj is BYE:
        logger.debug("Exiting")
        await signaling.close()
        return False
    elif isinstance(obj, aiortc.RTCSessionDescription):
        await pc.setRemoteDescription(obj)
        if obj.type == "offer":
            answer = await pc.createAnswer()
            if answer is None:
                return False
            # send answer
            await pc.setLocalDescription(answer)
            await signaling.send(pc.localDescription)
    elif isinstance(obj, aiortc.RTCIceCandidate):
        await pc.addIceCandidate(obj)
    return True
    

pc_channel: aiortc.RTCDataChannel|None = None
pc_track: aiortc.VideoStreamTrack|None = None
async def run_answer():
    signaling = TcpSocketSignaling(args.host, args.port)
    pc = aiortc.RTCPeerConnection()
    await signaling.connect()

    @pc.on("datachannel")
    def on_datachannel(channel: aiortc.RTCDataChannel):
        global pc_channel
        pc_channel = channel

    @pc.on("track")
    # Only accept the video stream track with image frames
    def on_track(track: aiortc.VideoStreamTrack):
        global pc_track
        pc_track = track

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            await pc.close()
            await signaling.close()
            pcs.discard(pc)

    frame_queue = multiprocessing.Queue() # Queues are thread and process safe.
    ball_x = multiprocessing.Value(ctypes.c_int, 0)
    ball_y = multiprocessing.Value(ctypes.c_int, 0)
    timestamp = multiprocessing.Value(ctypes.c_int, 0)
    multiprocessing.Process(
        target=process_a, 
        args=(frame_queue, ball_x, ball_y, timestamp),
        daemon=True,
    ).start()

    while await consume_signaling(pc, signaling):
        while pc_track:
            frame = await pc_track.recv()
            cv_frame = cv2.cvtColor(frame.to_ndarray(), cv2.COLOR_YUV2BGR_I420)
            frame_queue.put((frame.pts, cv_frame))
            cv2.imshow('client', cv_frame)
            cv2.waitKey(10)
            if pc_channel:
                data: str = json.dumps({
                    'pts': timestamp.value,
                    'x': ball_x.value,
                    'y': ball_y.value,
                })
                pc_channel.send(data)

pcs = set() 
async def on_shutdown():
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ball bounce client demo")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_answer())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(on_shutdown())
