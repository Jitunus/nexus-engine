# ==============================================================================
# MODULE: storage/wal.py
# DESCRIPTION: Write-Ahead Log (WAL) and Segment Storage for Persistence
# ==============================================================================

import os
import struct
import time
import hashlib
from typing import BinaryIO, List, Tuple, Optional

class WALRecord:
    __slots__ = ("lsn", "timestamp", "crc", "payload")

    def __init__(self, lsn: int, payload: bytes, timestamp: Optional[float] = None, crc: Optional[int] = None):
        self.lsn = lsn
        self.timestamp = timestamp or time.time()
        self.payload = payload
        self.crc = crc if crc is not None else self._calculate_crc()

    def _calculate_crc(self) -> int:
        h = hashlib.crc32(self.payload)
        return h

    def serialize(self) -> bytes:
        payload_len = len(self.payload)
        header = struct.pack("QdII", self.lsn, self.timestamp, self.crc, payload_len)
        return header + self.payload

    @classmethod
    def deserialize(cls, buffer: bytes) -> Tuple["WALRecord", int]:
        header_size = struct.calcsize("QdII")
        if len(buffer) < header_size:
            raise ValueError("Buffer too small for WAL record header.")
        
        lsn, timestamp, crc, payload_len = struct.unpack("QdII", buffer[:header_size])
        total_size = header_size + payload_len
        if len(buffer) < total_size:
            raise ValueError("Buffer truncated for WAL record payload.")
        
        payload = buffer[header_size:total_size]
        record = cls(lsn=lsn, payload=payload, timestamp=timestamp, crc=crc)
        
        if record._calculate_crc() != crc:
            raise ValueError(f"CRC mismatch for LSN {lsn}: expected {crc}, got {record._calculate_crc()}")
            
        return record, total_size


class WriteAheadLog:
    def __init__(self, directory: str, max_segment_size: int = 1024 * 1024):
        self.directory = directory
        self.max_segment_size = max_segment_size
        os.makedirs(directory, exist_ok=True)
        self.current_lsn = 0
        self._active_file: Optional[BinaryIO] = None
        self._open_active_segment()

    def _open_active_segment(self) -> None:
        segment_path = os.path.join(self.directory, f"{self.current_lsn:016d}.wal")
        self._active_file = open(segment_path, "a+b")

    def append(self, payload: bytes) -> int:
        record = WALRecord(lsn=self.current_lsn, payload=payload)
        data = record.serialize()
        
        self._active_file.write(data)
        self._active_file.flush()
        os.fsync(self._active_file.fileno())
        
        assigned_lsn = self.current_lsn
        self.current_lsn += 1
        return assigned_lsn

    def close(self) -> None:
        if self._active_file and not self._active_file.closed:
            self._active_file.close()
