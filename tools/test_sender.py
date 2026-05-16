#!/usr/bin/env python3
"""
Simulated iOS face capture sender for testing the Blender addon without a real device.
Sends synthetic face data over UDP with configurable animation patterns.

Usage:
    python test_sender.py [--host 192.168.1.255] [--port 49983] [--fps 60]
"""

import socket
import struct
import time
import math
import argparse

MAGIC = bytes([0xFA, 0xCE])
VERSION = 1
PACKET_TYPE_FACE = 0
BLENDSHAPE_COUNT = 52

ARKIT_NAMES = [
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
    "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
    "eyeWideLeft", "eyeWideRight",
    "jawForward", "jawLeft", "jawOpen", "jawRight",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthFunnel", "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight",
    "mouthPressLeft", "mouthPressRight", "mouthPucker", "mouthRight",
    "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
    "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight",
    "mouthUpperUpLeft", "mouthUpperUpRight",
    "noseSneerLeft", "noseSneerRight",
    "tongueOut",
]

INDEX = {name: i for i, name in enumerate(ARKIT_NAMES)}


def make_packet(seq: int, timestamp: float, blendshapes: list,
                head_quat: tuple, left_eye: tuple, right_eye: tuple) -> bytes:
    data = bytearray()
    data += MAGIC
    data += struct.pack('B', VERSION)
    data += struct.pack('B', PACKET_TYPE_FACE)
    data += struct.pack('<I', seq)
    data += struct.pack('<f', timestamp)
    data += struct.pack('<I', 1)  # flags: tracking valid

    for v in blendshapes:
        data += struct.pack('<f', v)

    for v in head_quat:
        data += struct.pack('<f', v)

    for v in left_eye:
        data += struct.pack('<f', v)

    for v in right_eye:
        data += struct.pack('<f', v)

    return bytes(data)


def animation_cycle(t: float) -> list:
    """Generate a natural-looking animation cycle cycling through expressions."""
    values = [0.0] * BLENDSHAPE_COUNT
    cycle_duration = 8.0
    phase = (t % cycle_duration) / cycle_duration

    # Blink every ~3 seconds
    blink_phase = (t % 3.0) / 3.0
    if 0.9 < blink_phase < 0.95:
        blink_val = math.sin((blink_phase - 0.9) / 0.05 * math.pi)
        values[INDEX["eyeBlinkLeft"]] = blink_val
        values[INDEX["eyeBlinkRight"]] = blink_val

    if phase < 0.25:
        # Smile
        p = math.sin(phase / 0.25 * math.pi) * 0.5 + 0.5
        values[INDEX["mouthSmileLeft"]] = p * 0.8
        values[INDEX["mouthSmileRight"]] = p * 0.8
        values[INDEX["cheekSquintLeft"]] = p * 0.4
        values[INDEX["cheekSquintRight"]] = p * 0.4
    elif phase < 0.5:
        # Mouth open (talking)
        p = (phase - 0.25) / 0.25
        values[INDEX["jawOpen"]] = abs(math.sin(p * math.pi * 4)) * 0.6
        values[INDEX["mouthFunnel"]] = abs(math.sin(p * math.pi * 3)) * 0.3
    elif phase < 0.75:
        # Surprise
        p = math.sin((phase - 0.5) / 0.25 * math.pi)
        values[INDEX["eyeWideLeft"]] = p * 0.7
        values[INDEX["eyeWideRight"]] = p * 0.7
        values[INDEX["browInnerUp"]] = p * 0.8
        values[INDEX["browOuterUpLeft"]] = p * 0.5
        values[INDEX["browOuterUpRight"]] = p * 0.5
        values[INDEX["jawOpen"]] = p * 0.4
    else:
        # Frown / angry
        p = math.sin((phase - 0.75) / 0.25 * math.pi)
        values[INDEX["browDownLeft"]] = p * 0.7
        values[INDEX["browDownRight"]] = p * 0.7
        values[INDEX["mouthFrownLeft"]] = p * 0.5
        values[INDEX["mouthFrownRight"]] = p * 0.5
        values[INDEX["noseSneerLeft"]] = p * 0.3
        values[INDEX["noseSneerRight"]] = p * 0.3

    return values


def head_animation(t: float) -> tuple:
    """Gentle head movement."""
    yaw = math.sin(t * 0.5) * 0.15
    pitch = math.sin(t * 0.3) * 0.1
    # Convert to quaternion (simplified euler to quat)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    w = cy * cp
    x = cy * sp
    y = sy * cp
    z = -sy * sp
    return (x, y, z, w)


def eye_animation(t: float) -> tuple:
    """Gentle eye look-around."""
    x = math.sin(t * 0.7) * 0.1
    y = math.sin(t * 0.5) * 0.05
    z = -1.0  # Looking forward (negative Z in ARKit)
    length = math.sqrt(x*x + y*y + z*z)
    return (x/length, y/length, z/length)


def main():
    parser = argparse.ArgumentParser(description="Simulate iOS face capture sender")
    parser.add_argument("--host", default="127.0.0.1", help="Target host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=49983, help="Target port (default: 49983)")
    parser.add_argument("--fps", type=int, default=60, help="Send rate in fps (default: 60)")
    parser.add_argument("--broadcast", action="store_true", help="Use broadcast mode")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.broadcast:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    interval = 1.0 / args.fps
    seq = 0
    start_time = time.time()

    print(f"Sending face data to {args.host}:{args.port} @ {args.fps}fps")
    print(f"Packet size: 264 bytes | Data rate: {264 * args.fps / 1024:.1f} KB/s")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            t = time.time() - start_time
            blendshapes = animation_cycle(t)
            head_quat = head_animation(t)
            left_eye = eye_animation(t)
            right_eye = eye_animation(t + 0.1)

            packet = make_packet(seq, t, blendshapes, head_quat, left_eye, right_eye)
            sock.sendto(packet, (args.host, args.port))

            seq += 1
            if seq % args.fps == 0:
                elapsed = time.time() - start_time
                print(f"\r  Sent: {seq} packets | Time: {elapsed:.1f}s | Expression: {get_expression_name(t)}", end="", flush=True)

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\nStopped. Total packets sent: {seq}")
    finally:
        sock.close()


def get_expression_name(t: float) -> str:
    cycle_duration = 8.0
    phase = (t % cycle_duration) / cycle_duration
    if phase < 0.25:
        return "Smile 😊"
    elif phase < 0.5:
        return "Talking 🗣️"
    elif phase < 0.75:
        return "Surprise 😮"
    else:
        return "Angry 😠"


if __name__ == "__main__":
    main()
