"""
Ball Bounce Server

This module contains a server implementation for a Pong game where a ball bounces
around in a 2D space. It utilizes the aiortc library to manage WebRTC communication
and cv2 for image/frame manipulation. Clients can connect to this server to
receive the ball's position and calculate the mean squared error of the ball's
position based on their calculations.

Attributes:
    DATA_CHANNEL (str): Name of the WebRTC data channel used for communication.
    logger (logging.Logger): Logger instance for logging events and errors.
    record (dict): Dictionary to store ball positions based on timestamps.
"""

import argparse
import asyncio
import json
import logging
import cv2
import random
import numpy as np

"""
HACK: It's necessary to run cv2.imshow once before importing VideoFrame and aiortc when deploying on dockers
"""
cv2.imshow("server", np.zeros((50, 50, 3)))

import aiortc
from av import VideoFrame
from aiortc.contrib.signaling import BYE, TcpSocketSignaling

DATA_CHANNEL = "dev-demo"

logger = logging.Logger("server")
record = dict()

class CircleFrame():
    """
    Represents a frame with drawable circles on a black background.
    
    This class provides utility methods to draw circles and convert the resulting
    image to a video frame format suitable for video streaming or processing.
    
    Attributes:
        w (int): Width of the frame.
        h (int): Height of the frame.
        rgb_array (np.ndarray): Array representing the RGB values of the frame.
    """
    def __init__(self):
        """
        Initializes the CircleFrame with a default width, height, and a black background.
        """
        # Initialize the window size
        self.w = 960
        self.h = 480
         # Black background supporting RGB
        self.rgb_array: np.ndarray = np.zeros((self.h, self.w, 3), dtype='uint8')

    def add_circle(self, x: int, y: int, r: int=20, 
                   color=(255, 255, 255), thickness:int=(-1)) -> 'CircleFrame':
        """
        Draws a circle on the frame at the specified coordinates.

        Args:
            x (int): The x-coordinate of the circle's center.
            y (int): The y-coordinate of the circle's center.
            r (int, optional): The radius of the circle. Defaults to 20.
            color (tuple, optional): The RGB color of the circle. Defaults to white.
            thickness (int, optional): Thickness of the circle outline. A negative value
                implies a filled circle. Defaults to -1 (filled circle).

        Returns:
            CircleFrame: The updated instance with the drawn circle.
        """
        cv2.circle(img=self.rgb_array, center=(x, y), 
            radius=r, color=color, thickness=thickness)
        return self

    def to_video_frame(self) -> VideoFrame:
        """
        Converts the frame with drawn circles into a video frame format.

        Returns:
            VideoFrame: The frame in a format suitable for video processing or streaming.
        """
        return VideoFrame.from_ndarray(self.rgb_array)


class BallBounce(aiortc.VideoStreamTrack):
    """
    A video stream track representing the ball's bouncing animation.
    
    This class simulates a ball bouncing within a 2D frame. The ball's movement is
    determined by updating its x and y coordinates, and frames representing the
    current position of the ball are generated.

    Attributes:
        frame (CircleFrame): The frame on which the ball's position is drawn.
        radius (int): The radius of the ball.
        x (int): The x-coordinate of the ball's center.
        x_shift (int): The horizontal shift applied to the ball in each frame.
        y (int): The y-coordinate of the ball's center.
        y_shift (int): The vertical shift applied to the ball in each frame.
    """
    def __init__(self):
        """
        Initializes the BallBounce class with a default radius and random starting position.
        """
        super().__init__()
        self.frame = CircleFrame()
        # Initialize the 2D ball bouncing simulation or animation.
        self.radius = 20
        self.x = random.randint(self.radius, self.frame.w-self.radius)
        self.x_shift = random.randint(1, self.frame.w//100)
        self.y = random.randint(self.radius, self.frame.h-self.radius)
        self.y_shift = random.randint(1, self.frame.h//100)

    async def _ball_update(self):
        """
        Updates the ball's position based on its current position and shift values.
        
        The method adjusts the position of the ball considering its radius and the frame 
        boundaries to ensure that it bounces back upon hitting the frame's edges.
        """
        if (self.x < self.radius) or self.x > (self.frame.w - self.radius):
            self.x_shift *= -1
        self.x += self.x_shift

        if (self.y < self.radius) or self.y > (self.frame.h - self.radius):
            self.y_shift *= -1
        self.y += self.y_shift

    async def recv(self) -> VideoFrame:
        """
        Generates and returns a frame showing the current position of the bouncing ball.
        
        The ball's position is updated, and then drawn on a fresh frame. Timestamp details 
        are also added to the frame before it is returned.

        Returns:
            VideoFrame: The frame showing the ball's current position.
        """
        await self._ball_update()
        frame = CircleFrame().add_circle(self.x, self.y, self.radius).to_video_frame()
        pts,  time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        record[pts] = np.array([self.x, self.y])
        return frame


async def consume_signaling(pc: aiortc.RTCPeerConnection, signaling: TcpSocketSignaling):
    """
    Consume signaling messages from the client.

    Args:
        pc (aiortc.RTCPeerConnection): Peer connection instance.
        signaling (TcpSocketSignaling): Signaling mechanism.

    Returns:
        bool: False if the received object is a BYE signal, else True.
    """
    obj = await signaling.receive()
    if obj is BYE:
        await signaling.close()
        return False
    elif isinstance(obj, aiortc.RTCSessionDescription):
        await pc.setRemoteDescription(obj)
    elif isinstance(obj, aiortc.RTCIceCandidate):
        await pc.addIceCandidate(obj)
    return True


pcs: set[aiortc.RTCPeerConnection] = set() 
async def on_shutdown():
    """Shutdown callback to close all peer connections."""
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


async def run_offer():
    """
    Run the offer routine for the WebRTC communication.

    Establishes a peer connection, sends an offer to the client, receives and 
    processes client's responses, and displays the calculated error.
    """
    pc = aiortc.RTCPeerConnection()
    channel = pc.createDataChannel(DATA_CHANNEL)
    pc.addTrack(BallBounce())
    pcs.add(pc)

    signaling = TcpSocketSignaling(args.host, args.port)

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)
    
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
        cv2.imshow("server", circle_frame.rgb_array)
        cv2.waitKey(2)
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
    # Argument parsing and main execution
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
