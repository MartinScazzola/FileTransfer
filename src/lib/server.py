import os
import socket
import threading
from lib.client_handler import ClientHandler
from lib.constants import *
from lib.file_parser import *
from lib.packet import Packet

class UDPServer:
    
        def __init__(self, server_address, protocol, logger):
            self.server_address = server_address
            self.client_handlers = {}
            self.protocol = protocol
            self.logger = logger
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
        def run_server(self, storage_path):

            if not os.path.exists("%s" % storage_path):
                os.makedirs(storage_path)
            
            try:
                self.sock.bind(self.server_address)
            except Exception as e:
                self.logger.error("Port already in use")
                raise e
                
            self.logger.info(f"Server starting up on: {self.server_address}")
            
            while True:
                
                data, address = self.sock.recvfrom(PACKET_SIZE)
                packet = Packet.from_bytes(data)
                if packet.is_syn():
                    filename_length = packet.get_payload()[0]
                    filename = packet.get_payload()[1:filename_length + 1].decode('utf-8')
                    handler = ClientHandler(
                        address,
                        packet.sequence_number,
                        self.protocol,
                        self.logger,
                        filename,
                        packet.is_download(),
                        storage_path
                        )

                    self.client_handlers[address] = handler
                    self.client_handlers[address].start()
                    self.logger.info(f"Created new handler with key {address}")
                else:
                    if(address in self.client_handlers):
                        self.client_handlers[address].enqueue(packet)
                self.verify_threads()

        def verify_threads(self):
            new_threads = {}
            for thread in self.client_handlers.values():
                if not thread.is_alive():
                    self.logger.debug(f"Deleted client thread {thread.address}")
                    del thread
                else:
                    new_threads[thread.address] = thread
            self.client_handlers = new_threads                    


        def closeInterrupt(self):
            self.sock.close()
        
        def __del__(self):
            self.logger.debug("Closing client threads")
            for thread in self.client_handlers.values():
                del thread
            self.logger.info("Server stopped correctly")