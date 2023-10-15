from collections import defaultdict
import pytest

from client.client import *

@pytest.mark.asyncio     
async def test_consume_signaling_candidate():
    """
    Test case for consuming a signaling event with a candidate.

    This test verifies that when a candidate is received through the signaling process, 
    the `consume_signaling` function correctly handles it and returns `True`.

    - A mock peer connection (`MockPC`) and a mock RTCIceCandidate (`aiortc.RTCIceCandidate`) are created.
    - A mock signaling process (`MockTCPSignaling`) is also set up to receive the mock candidate.
    - The `consume_signaling` function is called with the mock peer connection and mock signaling.
    - The response of the `consume_signaling` function should be `True` to indicate successful handling.
    """
    # Arrange
    mock_pc = MockPC()
    mock_candidate = aiortc.RTCIceCandidate
    mock_candidate_signaling = MockTCPSignaling({'receive': mock_candidate})
    # Act
    response = await consume_signaling(mock_pc, mock_candidate_signaling)
    # Assert
    assert response == True

@pytest.mark.asyncio     
async def test_consume_signaling_exit():
    """
    Test case to validate the behavior when receiving an exit signal.
    """
    # Arrange
    mock_pc = MockPC()
    mock_bye_signaling = MockTCPSignaling({'receive': BYE})
    # Act
    response = await consume_signaling(mock_pc, mock_bye_signaling)
    # Assert
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_no_answer():
    """
    Test case to validate the behavior when there's no answer received after offering a session description.
    """
    mock_description = aiortc.RTCSessionDescription('', type='offer')
    mock_pc = MockPC({'createAnswer': None}, 
                     {'setRemoteDescription': mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description})
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == False

@pytest.mark.asyncio     
async def test_consume_signaling_wrong_type():
    """
    Test case to validate the behavior when receiving a session description of unexpected type.
    """
    mock_description = aiortc.RTCSessionDescription
    mock_pc = MockPC(assertions={'setRemoteDescription': mock_description})
    mock_description_signaling = MockTCPSignaling({'receive': mock_description})
    response = await consume_signaling(mock_pc, mock_description_signaling)
    assert response == True

class MockPC(aiortc.RTCPeerConnection):
    """
    Mock object for simulating the behavior of the RTCPeerConnection class.

    This class is primarily used for testing the signaling process in WebRTC.
    It overrides methods to return predefined results (stubs) and validate inputs
    against expected values (assertions).

    Attributes:
    - stubs: Dictionary containing predefined responses for specific methods.
    - assertions: Dictionary containing expected input values for specific methods.
    """
    def __init__(self, stubs: dict=defaultdict(None), 
                 assertions: dict=defaultdict(None)) -> None:
        self.stubs = stubs
        self.assertions = assertions

    async def setRemoteDescription(self, obj):
        """Mocks the setRemoteDescription method with predefined assertions."""
        assert obj == self.assertions['setRemoteDescription']

    async def setLocalDescription(self, obj):
        """Mocks the setLocalDescription method with predefined assertions."""
        assert obj == self.assertions['setLocalDescription']

    async def addIceCandidate(self, obj):
        """Mocks the addIceCandidate method with predefined assertions."""
        assert obj == self.assertions['addIceCandidate']

    async def close(self):
        """Mocks the close method with a pass-through implementation."""
        pass

    async def createAnswer(self):
        """Mocks the createAnswer method by returning predefined stub response."""
        return self.stubs['createAnswer']

class MockTCPSignaling(TcpSocketSignaling):
    """
    Mock object for simulating the behavior of the TcpSocketSignaling class.

    This class is primarily used for testing the signaling process.
    It overrides methods to return predefined results (stubs) and validate inputs
    against expected values (assertions).

    Attributes:
    - stubs: Dictionary containing predefined responses for specific methods.
    - assertions: Dictionary containing expected input values for specific methods.
    """
    def __init__(self, stubs: dict=defaultdict(None), 
                 assertions: dict=defaultdict(None)) -> None:
        self.stubs = stubs
        self.assertions = assertions

    async def receive(self):
        """Mocks the receive method by returning predefined stub response."""
        return self.stubs['receive']
    
    async def close(self):
        """Mocks the close method with a pass-through implementation."""
        pass
    async def send(self, obj):
        """Mocks the send method with predefined assertions."""
        assert obj == self.assertions['send']
