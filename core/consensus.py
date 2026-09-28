# ==============================================================================
# MODULE: core/consensus.py
# DESCRIPTION: Raft-style Leader Election and State Machine Consensus
# ==============================================================================

import random
import time
from typing import List, Optional

class NodeState:
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class ConsensusNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.state = NodeState.FOLLOWER
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(0.150, 0.300)

    def become_candidate(self) -> None:
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()

    def receive_heartbeat(self, term: int, leader_id: str) -> bool:
        if term >= self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.last_heartbeat = time.time()
            return True
        return False

    def check_timeout(self) -> bool:
        if self.state == NodeState.LEADER:
            return False
        if time.time() - self.last_heartbeat > self.election_timeout:
            return True
        return False
