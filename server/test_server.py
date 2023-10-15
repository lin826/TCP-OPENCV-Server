from collections import defaultdict
import pytest
import numpy as np

from av import VideoFrame
from server.server import *

def test_CircleFrame():
    """
    Test if a CircleFrame object correctly converts to a VideoFrame object
    and if the shape of the ndarray of the VideoFrame is as expected.
    """
    # Arrange
    circle_frame: CircleFrame = CircleFrame()
    # Act
    video_frame = circle_frame.to_video_frame()
    # Assert
    assert video_frame.to_ndarray().shape == (circle_frame.h, circle_frame.w, 3)

def test_CircleFrame_exceeding():
    """
    Test if adding a circle out of the frame's boundaries 
    doesn't alter the frame's content.
    """
    # Circle not in the frame
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(-1, -1, 0, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 0

def test_CircleFrame_one_pixel():
    """
    Test if adding a one-pixel circle correctly alters the frame's content.
    """
    # 3 (RGB dimensions) * 1 (middle)
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(0, 0, 0, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 3

def test_CircleFrame_three_pixel():
    """
    Test if adding a circle with a radius of one pixel 
    correctly alters the frame's content.
    """
    # 3 (RGB dimensions) * 3 (middle, down, right)
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(0, 0, 1, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 9

@pytest.mark.asyncio
async def test_BallBounce():
    """
    Test if a BallBounce object correctly returns a VideoFrame 
    with the expected timestamp, array shape, and record length.
    """
    ball_bounce = BallBounce()
    # Get the request for a new image frame
    video_frame = await ball_bounce.recv()
    assert video_frame.pts >= 0 # timestamp
    assert video_frame.to_ndarray().shape[2] == 3 # RGB
    assert len(record) == 1 # Add one record row

@pytest.mark.asyncio
async def test_BallBounce_radius():
    """
    Test if a BallBounce object with a one-pixel radius 
    correctly returns a VideoFrame with the expected content, timestamp, and record length.
    """
    ball_bounce = BallBounce()
    # Get the request for a one-pixel ball image frame
    ball_bounce.radius = 0
    video_frame = await ball_bounce.recv()
    assert np.count_nonzero(video_frame.to_ndarray()) == 3 # RGB
    assert video_frame.pts >= 0 # timestamp
    assert len(record) == 1 # Add another record row

@pytest.mark.asyncio     
async def test_consume_signaling_exit():
    """
    Test if consume_signaling function correctly handles a BYE signal 
    and returns the expected response.
    """
    # Arrange
    mock_pc = MockPC()
    mock_bye_signaling = MockTCPSignaling({'receive': BYE})
    # Act
    response = await consume_signaling(mock_pc, mock_bye_signaling)
    # Assert
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_offer():
    """
    Test if consume_signaling function correctly handles an offer signal 
    and returns the expected response.
    """
    mock_description = aiortc.RTCSessionDescription
    mock_pc = MockPC(assertions={'setRemoteDescription':mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description})
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == True

@pytest.mark.asyncio     
async def test_consume_signaling_candidate():
    """
    Test if consume_signaling function correctly handles a candidate signal 
    and returns the expected response.
    """
    mock_candidate = aiortc.RTCIceCandidate
    mock_pc = MockPC(assertions={'addIceCandidate':mock_candidate})
    mock_candidate_signaling = MockTCPSignaling({'receive': mock_candidate})
    response = await consume_signaling(mock_pc, mock_candidate_signaling)
    assert response == True

@pytest.mark.asyncio
async def test_on_shutdown():
    """
    Test if the on_shutdown function correctly closes all peer connections.
    """
    global pcs
    pcs.add(MockPC())
    pcs.add(MockPC())
    assert len(pcs) == 2
    await on_shutdown()
    assert len(pcs) == 0

class MockPC(aiortc.RTCPeerConnection):
    """
    Mock class for RTCPeerConnection to simulate and validate various peer connection behaviors.

    Attributes:
        stubs (dict): A dictionary containing predefined responses for specific methods.
        assertions (dict): A dictionary containing predefined expected values to validate
                           the behavior of specific methods.

    Methods:
        setRemoteDescription: Simulates setting a remote description and checks against
                              expected values.
        addIceCandidate: Simulates adding an ICE candidate and checks against expected values.
        close: Simulates closing the connection.
    """
    def __init__(self, stubs: dict=defaultdict(None), 
                 assertions: dict=defaultdict(None)) -> None:
        self.stubs = stubs
        self.assertions = assertions
    async def setRemoteDescription(self, obj):
        assert obj == self.assertions['setRemoteDescription']
    async def addIceCandidate(self, obj):
        assert obj == self.assertions['addIceCandidate']
    async def close(self):
        pass

class MockTCPSignaling(TcpSocketSignaling):
    """
    Mock class for TcpSocketSignaling to simulate and validate signaling behaviors.

    Attributes:
        stubs (dict): A dictionary containing predefined responses for specific methods.
        assertions (dict): A dictionary containing predefined expected values to validate
                           the behavior of specific methods.

    Methods:
        receive: Simulates receiving data and returns the stubbed response.
        close: Simulates closing the signaling connection.
        send: Simulates sending data and checks against expected values.
    """
    def __init__(self, stubs: dict=defaultdict(None), 
                 assertions: dict=defaultdict(None)) -> None:
        self.stubs = stubs
        self.assertions = assertions
    async def receive(self):
        return self.stubs['receive']
    async def close(self):
        pass
    async def send(self, obj):
        assert obj == self.assertions['send']
