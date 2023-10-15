import pytest

from client.client import *

def test_process_a():
    pass
    # process_a()

# @pytest.mark.asyncio     
# async def test_consume_signaling_exit():
#     # Arrange
#     mock_pc = MockPC(defaultdict(None))
#     mock_bye_signaling = MockTCPSignaling({'receive': BYE}, {})
#     # Act
#     response = await consume_signaling(mock_pc, mock_bye_signaling)
#     # Assert
#     assert response == False

# @pytest.mark.asyncio     
# async def test_consume_signaling_offer():
#     mock_pc = MockPC({})
#     mock_description = aiortc.RTCSessionDescription
#     mock_description_signaling = MockTCPSignaling({'receive': mock_description}, {})
#     response = await consume_signaling(mock_pc, mock_description_signaling)
#     assert response == True

# @pytest.mark.asyncio     
# async def test_consume_signaling_candidate():
#     mock_pc = MockPC({})
#     mock_candidate = aiortc.RTCIceCandidate
#     mock_candidate_signaling = MockTCPSignaling({'receive': mock_candidate}, {})
#     response = await consume_signaling(mock_pc, mock_candidate_signaling)
#     assert response == True

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
