import socket
import struct
import threading

class SocketManager:
    def __init__(self, local_ip, local_port, data_callback):
        self.local_ip = local_ip
        self.local_port = local_port
        self.data_callback = data_callback  # Callback to send data to the GUI
        self.socket = None
        self.is_listening = False
        self.thread = None

    def connect(self):
        if not self.is_listening:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.local_ip, self.local_port))
            self.is_listening = True
            self.thread = threading.Thread(target=self.listen, daemon=True)
            self.thread.start()

    def disconnect(self):
        self.is_listening = False
        if self.socket:
            self.socket.close()

    def listen(self):
        while self.is_listening:
            try:
                header_data, _ = self.socket.recvfrom(256)
                data_packet, _ = self.socket.recvfrom(1012)
                self.data_callback(header_data, data_packet)
            except Exception as e:
                print(f"Socket error: {e}")

    def is_connected(self):
        return self.is_listening
