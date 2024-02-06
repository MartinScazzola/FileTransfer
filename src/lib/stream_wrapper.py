from lib.constants import PACKET_SIZE, TIMEOUT
from lib.packet import Packet


class StreamWrapper:
    def __init__(self, socket, queue):
        self.socket = socket
        self.queue = queue
        self.socket.settimeout(TIMEOUT)
    
    def receive(self):
        if self.queue is None:
            return Packet.from_bytes(self.socket.recv(PACKET_SIZE))
        else:
            return self.queue.get(True, TIMEOUT)
    
    def send_to(self, bytes, address):
        self.socket.sendto(bytes, address)

    def close(self):
        self.socket.close()
    
    def enqueue(self, packet):
        self.queue.put(packet)