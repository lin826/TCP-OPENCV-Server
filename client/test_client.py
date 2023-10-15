from collections import defaultdict
import pytest

from client.client import *

@pytest.mark.asyncio     
async def test_consume_signaling_exit():
    # Arrange
    mock_pc = MockPC()
    mock_bye_signaling = MockTCPSignaling({'receive': BYE})
    # Act
    response = await consume_signaling(mock_pc, mock_bye_signaling)
    # Assert
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_no_answer():
    mock_description = aiortc.RTCSessionDescription('', type='offer')
    mock_pc = MockPC({'createAnswer': None}, 
                     {'setRemoteDescription': mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description})
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_wrong_type():
    mock_description = aiortc.RTCSessionDescription
    mock_pc = MockPC(assertions={'setRemoteDescription': mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description})
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == True

@pytest.mark.asyncio     
async def test_consume_signaling_candidate():
    mock_pc = MockPC()
    mock_candidate = aiortc.RTCIceCandidate
    mock_candidate_signaling = MockTCPSignaling({'receive': mock_candidate})
    response = await consume_signaling(mock_pc, mock_candidate_signaling)
    assert response == True

class MockPC(aiortc.RTCPeerConnection):
    def __init__(self, stubs: dict=defaultdict(None), 
                 assertions: dict=defaultdict(None)) -> None:
        self.stubs = stubs
        self.assertions = assertions
    async def setRemoteDescription(self, obj):
        assert obj == self.assertions['setRemoteDescription']
    async def setLocalDescription(self, obj):
        assert obj == self.assertions['setLocalDescription']
    async def addIceCandidate(self, obj):
        assert obj == self.assertions['addIceCandidate']
    async def close(self):
        pass
    async def createAnswer(self):
        return self.stubs['createAnswer']

class MockTCPSignaling(TcpSocketSignaling):
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
