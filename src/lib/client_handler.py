import os
from socket import *
from threading import Thread as thread
import queue
from lib.constants import *
from lib.exceptions import MaximumRetriesError
from lib.packet import Packet
from lib.selective_repeat import SelectiveRepeat
from lib.stream_wrapper import StreamWrapper
from lib.stop_and_wait import StopAndWait

class ClientHandler(thread):
    def __init__(
        self,
        client_address,
        sequence_number_client,
        protocol,
        logger,
        filename,
        is_download,
        storage_path
    ):
        self.file = None
        self.address = client_address
        self.sequence_number_client = sequence_number_client
        self.stream = StreamWrapper(socket(AF_INET, SOCK_DGRAM), queue.Queue())
        self.logger = logger
        self.filename = filename
        self.is_download = is_download
        self.protocol = StopAndWait(self.address, self.logger) if protocol == SAW_PROTOCOL else SelectiveRepeat(self.address, self.logger)
        self.storage_path = storage_path
        thread.__init__(self)
   

    def run(self):
        self.protocol.response_handshake(self.stream, self.address, self.sequence_number_client)
        try:
            if self.is_download:
                self.send_file()
            else:
                self.receive_file()
        except:
            self.logger.error("Client handler exception")


    def send_file(self):
        with open(self.storage_path + self.filename, 'rb') as file:  
            data = file.read(PAYLOAD_SIZE)
            while data:
                packet = Packet.new_reg_packet(data, DOWNLOAD)
                packet.download = DOWNLOAD

                self.protocol.send_packet(packet, self.stream)
                data = file.read(PAYLOAD_SIZE)
            fin_packet = Packet.new_fin_packet()
            self.protocol.send_packet(fin_packet, self.stream)
        
        self.logger.info("Download completed")
    
    def receive_file(self):
        with open(self.storage_path + self.filename, "wb") as file:  
            while True:
                try:
                    packet = self.protocol.recv_packet(self.stream)
                    if packet.is_fin():
                        break
                    file.write(packet.get_payload())
                
                except MaximumRetriesError as e:
                    os.remove(self.storage_path + self.filename) 
                    self.logger.info(f"Exception occurred: {e}, incomplete file removed")
                    return

        self.logger.info("Upload completed")
        
    def enqueue(self, packet):
        self.stream.enqueue(packet)
    
    def is_alive(self):
        return super().is_alive()