from collections import defaultdict
import pytest
import numpy as np

from av import VideoFrame
from server.server import *

def test_CircleFrame():
    # Arrange
    circle_frame: CircleFrame = CircleFrame()
    # Act
    video_frame = circle_frame.to_video_frame()
    # Assert
    assert video_frame.to_ndarray().shape == (circle_frame.h, circle_frame.w, 3)

def test_CircleFrame_exceeding():
    # Circle not in the frame
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(-1, -1, 0, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 0

def test_CircleFrame_one_pixel():
    # 3 (RGB dimensions) * 1 (middle)
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(0, 0, 0, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 3

def test_CircleFrame_three_pixel():
    # 3 (RGB dimensions) * 3 (middle, down, right)
    circle_frame: CircleFrame = CircleFrame()
    circle_frame = circle_frame.add_circle(0, 0, 1, color=(1,1,1))
    assert np.sum(circle_frame.rgb_array) == 9

@pytest.mark.asyncio
async def test_BallBounce():
    ball_bounce = BallBounce()
    # Get the request for a new image frame
    video_frame = await ball_bounce.recv()
    assert video_frame.pts >= 0 # timestamp
    assert video_frame.to_ndarray().shape[2] == 3 # RGB
    assert len(record) == 1 # Add one record row

@pytest.mark.asyncio
async def test_BallBounce_radius():
    ball_bounce = BallBounce()
    # Get the request for a one-pixel ball image frame
    ball_bounce.radius = 0
    video_frame = await ball_bounce.recv()
    assert np.count_nonzero(video_frame.to_ndarray()) == 3 # RGB
    assert video_frame.pts >= 0 # timestamp
    assert len(record) == 1 # Add another record row

@pytest.mark.asyncio     
async def test_consume_signaling_exit():
    # Arrange
    mock_pc = MockPC(defaultdict(None))
    mock_bye_signaling = MockTCPSignaling({'receive': BYE}, defaultdict(None))
    # Act
    response = await consume_signaling(mock_pc, mock_bye_signaling)
    # Assert
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_offer():
    mock_description = aiortc.RTCSessionDescription
    mock_pc = MockPC({'setRemoteDescription':mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description}, defaultdict(None))
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == True

@pytest.mark.asyncio     
async def test_consume_signaling_candidate():
    mock_candidate = aiortc.RTCIceCandidate
    mock_pc = MockPC({'addIceCandidate':mock_candidate})
    mock_candidate_signaling = MockTCPSignaling({'receive': mock_candidate}, defaultdict(None))
    response = await consume_signaling(mock_pc, mock_candidate_signaling)
    assert response == True

@pytest.mark.asyncio
async def test_on_shutdown():
    global pcs
    pcs.add(MockPC({}))
    pcs.add(MockPC({}))
    assert len(pcs) == 2
    await on_shutdown()
    assert len(pcs) == 0

class MockPC(aiortc.RTCPeerConnection):
    def __init__(self, assertions: dict) -> None:
        self.assertions = assertions
    async def setRemoteDescription(self, obj):
        assert obj == self.assertions['setRemoteDescription']
    async def addIceCandidate(self, obj):
        assert obj == self.assertions['addIceCandidate']
    async def close(self):
        pass

class MockTCPSignaling(TcpSocketSignaling):
    def __init__(self, stubs: dict, assertions: dict) -> None:
        self.stubs = stubs
        self.assertions = assertions
    async def receive(self):
        return self.stubs['receive']
    async def close(self):
        pass
    async def send(self, obj):
        assert obj == self.assertions['send']