import argparse
import asyncio
import json
import logging
import uuid
import cv2
import random
import numpy as np

im = np.random.random((800, 800, 3))
cv2.imshow("server", im)
cv2.waitKey(1)

from av import VideoFrame
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import BYE, TcpSocketSignaling

DATA_CHANNEL = "dev-demo"

logger = logging.Logger("pong")
record = dict()

class CircleFrame():
    def __init__(self):
        # Initialize the window size
        self.w = 960
        self.h = 480
         # Black background supporting RGB
        self.rgb_array: np.ndarray = np.zeros((self.h, self.w, 3), dtype='uint8')

    def add_circle(self, x: int, y: int, r: int=20, 
                   color=(255, 255, 255), thickness:int=(-1)):
        cv2.circle(img=self.rgb_array, center=(x, y), 
            radius=r, color=color, thickness=thickness)
        return self

    def to_video_frame(self) -> VideoFrame:
        return VideoFrame.from_ndarray(self.rgb_array)


class BallBounce(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.frame = CircleFrame()
        # Initialize the 2D ball bouncing simulation or animation.
        self.radius = 20
        self.x = random.randint(self.radius, self.frame.w-self.radius)
        self.x_shift = random.randint(1, self.frame.w//100)
        self.y = random.randint(self.radius, self.frame.h-self.radius)
        self.y_shift = random.randint(1, self.frame.h//100)

    async def _ball_update(self):
        if (self.x < self.radius) or self.x > (self.frame.w - self.radius):
            self.x_shift *= -1
        self.x += self.x_shift

        if (self.y < self.radius) or self.y > (self.frame.h - self.radius):
            self.y_shift *= -1
        self.y += self.y_shift

    async def recv(self):
        # Generate and return the frame of the ball bouncing.
        # Use cv2 to create the image/frame.
        await self._ball_update()
        frame = CircleFrame().add_circle(self.x, self.y, self.radius).to_video_frame()
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        record[pts] = np.array([self.x, self.y])
        return frame


async def consume_signaling(pc, signaling):
    obj = await signaling.receive()
    if obj is BYE:
        await signaling.close()
        return False
    elif isinstance(obj, RTCSessionDescription):
        print("Got remote description")
        await pc.setRemoteDescription(obj)
    elif isinstance(obj, RTCIceCandidate):
        print("Got ICE")
        await pc.addIceCandidate(obj)
    return True


pcs = set() 
async def on_shutdown():
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


async def run_offer():
    pc = RTCPeerConnection()
    channel = pc.createDataChannel(DATA_CHANNEL)
    pc.addTrack(BallBounce())
    pcs.add(pc)

    signaling = TcpSocketSignaling(args.host, args.port)

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)
    print("Sent local description")
    
    def on_message(message):
        # Calculate error and display
        logger.info(f"{channel.label} - message received: {message}")
        data = json.loads(message)
        global record
        if data['pts'] not in record:
            logger.error(f"{channel.label} - pts not found.")
            print(record)
            return
        # Mean Square Error (MSE)
        record_xy = record.pop(data['pts'])
        err = np.mean((record_xy - np.array([data['x'], data['y']]))**2)
        logger.warning(f"MSE={err}, between {(data['x'], data['y'])} and {record_xy}")
        # Redness reflects the value of MSE.
        color = [max(100, 255 - err)] * 2 + [255]
        circle_frame = CircleFrame().add_circle(data['x'], data['y'], color=color)
        try:
            cv2.imshow("server", circle_frame.rgb_array)
            cv2.waitKey(1)
            # im = np.random.random((800, 800, 3))
            # cv2.imshow("img", im)
            # cv2.waitKey(1)
            # asyncio.sleep(3)
            pass        
        except Exception as e:
            print("Exception", e)
    channel.add_listener("message", on_message)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            await signaling.close()
            await pc.close()
            pcs.discard(pc)

    while True:
        await consume_signaling(pc, signaling)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ball bounce server demo")
    parser.add_argument("--host", default='0.0.0.0', help="Host for HTTP server (default: 0.0.0.0)")
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
        loop.run_until_complete(run_offer())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(on_shutdown())
