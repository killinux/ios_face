import struct
from dataclasses import dataclass, field
from typing import Optional
from .arkit_constants import PACKET_MAGIC, PACKET_VERSION, PACKET_SIZE, BLENDSHAPE_COUNT


@dataclass
class FaceData:
    sequence: int = 0
    timestamp: float = 0.0
    flags: int = 0
    blendshapes: list = field(default_factory=lambda: [0.0] * BLENDSHAPE_COUNT)
    head_quaternion: tuple = (0.0, 0.0, 0.0, 1.0)  # x, y, z, w
    left_eye_direction: tuple = (0.0, 0.0, 0.0)
    right_eye_direction: tuple = (0.0, 0.0, 0.0)

    @property
    def is_tracking(self):
        return bool(self.flags & 1)


def decode_packet(data: bytes) -> Optional[FaceData]:
    if len(data) < PACKET_SIZE:
        return None

    if data[0:2] != PACKET_MAGIC:
        return None

    if data[2] != PACKET_VERSION:
        return None

    face_data = FaceData()
    offset = 4

    face_data.sequence = struct.unpack_from('<I', data, offset)[0]
    offset += 4

    face_data.timestamp = struct.unpack_from('<f', data, offset)[0]
    offset += 4

    face_data.flags = struct.unpack_from('<I', data, offset)[0]
    offset += 4

    face_data.blendshapes = list(struct.unpack_from(f'<{BLENDSHAPE_COUNT}f', data, offset))
    offset += BLENDSHAPE_COUNT * 4

    face_data.head_quaternion = struct.unpack_from('<4f', data, offset)
    offset += 16

    face_data.left_eye_direction = struct.unpack_from('<3f', data, offset)
    offset += 12

    face_data.right_eye_direction = struct.unpack_from('<3f', data, offset)

    return face_data
