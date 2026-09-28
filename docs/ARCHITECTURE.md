# NexusEngine Architecture Specification

## 1. System Overview
NexusEngine is a distributed, fault-tolerant event stream processing and consensus engine. It decouples high-throughput log persistence from state consensus and network framing.

## 2. Core Subsystems
- **Write-Ahead Log (storage/wal.py)**: Implements durable binary persistence using segment rotation, LSN tracking, and CRC32 payload validation.
- **Binary Network Protocol (network/protocol.py)**: Custom length-prefixed framing codec with magic byte validation (0xFA).
- **Raft Consensus (core/consensus.py)**: Lightweight state machine handling node states and randomized election timeouts.
