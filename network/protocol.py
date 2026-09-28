# ==============================================================================
# MODULE: network/protocol.py
# DESCRIPTION: Binary Framing and RPC Protocol for Node-to-Node Communication
# ==============================================================================

import struct
import json
from typing import Dict, Any, Tuple

class MessageType:
    PING = 0x01
    PONG = 0x02
    PRODUCE = 0x10
    PRODUCE_ACK = 0x11
    CONSUME = 0x20
    CONSUME_RESP = 0x21

class ProtocolCodec:
    @staticmethod
    def encode(msg_type: int, payload: Dict[str, Any]) -> bytes:
        body = json.dumps(payload).encode('utf-8')
        body_len = len(body)
        # Format: Magic Byte (B), Message Type (B), Body Length (I), Body (bytes)
        header = struct.pack("BBI", 0xFA, msg_type, body_len)
        return header + body

    @staticmethod
    def decode(buffer: bytes) -> Tuple[int, Dict[str, Any], int]:
        header_size = struct.calcsize("BBI")
        if len(buffer) < header_size:
            raise ValueError("Buffer too small for protocol header.")
        
        magic, msg_type, body_len = struct.unpack("BBI", buffer[:header_size])
        if magic != 0xFA:
            raise ValueError(f"Invalid magic byte: {hex(magic)}")
            
        total_size = header_size + body_len
        if len(buffer) < total_size:
            raise ValueError("Buffer truncated for message body.")
            
        body_bytes = buffer[header_size:total_size]
        payload = json.loads(body_bytes.decode('utf-8'))
        return msg_type, payload, total_size
