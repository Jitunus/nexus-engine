# ==============================================================================
# MODULE: tests/test_consensus.py
# DESCRIPTION: Unit Tests for Consensus Node and Leader Election Logic
# ==============================================================================

import time
import pytest
from core.consensus import ConsensusNode, NodeState

def test_node_initialization():
    node = ConsensusNode(node_id="node-1", peers=["node-2", "node-3"])
    assert node.node_id == "node-1"
    assert node.state == NodeState.FOLLOWER
    assert node.current_term == 0
    assert node.voted_for is None

def test_become_candidate():
    node = ConsensusNode(node_id="node-1", peers=["node-2", "node-3"])
    node.become_candidate()
    assert node.state == NodeState.CANDIDATE
    assert node.current_term == 1
    assert node.voted_for == "node-1"

def test_receive_heartbeat_updates_state():
    node = ConsensusNode(node_id="node-1", peers=["node-2"])
    node.become_candidate()
    
    success = node.receive_heartbeat(term=1, leader_id="node-2")
    assert success is True
    assert node.state == NodeState.FOLLOWER
    assert node.current_term == 1
    assert node.voted_for is None

def test_election_timeout_trigger():
    node = ConsensusNode(node_id="node-1", peers=["node-2"])
    node.election_timeout = 0.01  # set very short timeout
    time.sleep(0.02)
    assert node.check_timeout() is True
