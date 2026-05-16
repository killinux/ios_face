import socket
import threading
from typing import Optional
from .packet_decoder import decode_packet, FaceData


class UDPReceiver:
    def __init__(self, port=49983):
        self.port = port
        self._socket = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_data: Optional[FaceData] = None
        self.packets_received = 0
        self.packets_dropped = 0
        self._last_sequence = -1

    def start(self):
        if self._running:
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', self.port))
        self._socket.settimeout(0.5)

        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._socket:
            self._socket.close()
            self._socket = None

    def get_latest(self) -> Optional[FaceData]:
        with self._lock:
            return self._latest_data

    @property
    def is_running(self):
        return self._running

    def _receive_loop(self):
        while self._running:
            try:
                data, addr = self._socket.recvfrom(512)
                face_data = decode_packet(data)
                if face_data is None:
                    continue

                self.packets_received += 1

                if self._last_sequence >= 0:
                    expected = self._last_sequence + 1
                    if face_data.sequence > expected:
                        self.packets_dropped += face_data.sequence - expected
                self._last_sequence = face_data.sequence

                with self._lock:
                    self._latest_data = face_data

            except socket.timeout:
                continue
            except OSError:
                break
