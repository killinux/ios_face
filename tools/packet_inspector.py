#!/usr/bin/env python3
"""
UDP packet inspector for debugging face capture data stream.
Listens on the specified port and prints decoded packet contents.

Usage:
    python packet_inspector.py [--port 49983] [--verbose]
"""

import socket
import struct
import argparse
import time

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


def decode_and_print(data: bytes, verbose: bool, addr: tuple):
    if len(data) < 264:
        print(f"  [WARN] Short packet: {len(data)} bytes from {addr}")
        return

    magic = data[0:2]
    if magic != bytes([0xFA, 0xCE]):
        print(f"  [WARN] Bad magic: {magic.hex()} from {addr}")
        return

    version = data[2]
    pkt_type = data[3]
    seq = struct.unpack_from('<I', data, 4)[0]
    timestamp = struct.unpack_from('<f', data, 8)[0]
    flags = struct.unpack_from('<I', data, 12)[0]

    blendshapes = list(struct.unpack_from('<52f', data, 16))
    head_quat = struct.unpack_from('<4f', data, 224)
    left_eye = struct.unpack_from('<3f', data, 240)
    right_eye = struct.unpack_from('<3f', data, 252)

    tracking = "OK" if flags & 1 else "LOST"

    print(f"\n--- Packet #{seq} | t={timestamp:.3f}s | tracking={tracking} | from {addr[0]} ---")
    print(f"  Head: quat({head_quat[0]:.3f}, {head_quat[1]:.3f}, {head_quat[2]:.3f}, {head_quat[3]:.3f})")
    print(f"  Eyes: L({left_eye[0]:.3f}, {left_eye[1]:.3f}, {left_eye[2]:.3f}) "
          f"R({right_eye[0]:.3f}, {right_eye[1]:.3f}, {right_eye[2]:.3f})")

    # Show active blendshapes (value > 0.05)
    active = [(ARKIT_NAMES[i], v) for i, v in enumerate(blendshapes) if v > 0.05]
    if active:
        print(f"  Active blendshapes ({len(active)}):")
        for name, val in sorted(active, key=lambda x: -x[1]):
            bar = "#" * int(val * 20)
            print(f"    {name:24s} {val:.3f} |{bar}")
    elif verbose:
        print("  No active blendshapes")


def main():
    parser = argparse.ArgumentParser(description="Face capture packet inspector")
    parser.add_argument("--port", type=int, default=49983, help="Port to listen on")
    parser.add_argument("--verbose", action="store_true", help="Show all details")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', args.port))

    print(f"Listening for face capture packets on port {args.port}...")
    print("Press Ctrl+C to stop\n")

    packet_count = 0
    start_time = time.time()

    try:
        while True:
            data, addr = sock.recvfrom(512)
            packet_count += 1

            if args.verbose or packet_count % 60 == 1:
                decode_and_print(data, args.verbose, addr)
            elif packet_count % 60 == 0:
                elapsed = time.time() - start_time
                print(f"\r  Received: {packet_count} packets | {packet_count/elapsed:.0f} pps", end="", flush=True)
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\nTotal: {packet_count} packets in {elapsed:.1f}s ({packet_count/elapsed:.0f} pps)")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
