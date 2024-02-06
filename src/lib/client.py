import os
import socket
import time

from lib.constants import *
from lib.exceptions import MaxSizeFileError, MaximumRetriesError
from lib.packet import Packet
from lib.selective_repeat import SelectiveRepeat
from lib.stop_and_wait import StopAndWait
from lib.stream_wrapper import StreamWrapper

class UDPClient:
    
        def __init__(self, server_address, protocol, logger):
            self.server_address = server_address
            self.logger = logger
            self.stream = StreamWrapper(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), None)
            self.protocol = StopAndWait(self.server_address, self.logger) if protocol == SAW_PROTOCOL else SelectiveRepeat(self.server_address, self.logger)

        def download_file(self, file_name, save_path):
            self.logger.info(f"Downloading {file_name} from Server to {save_path + file_name}")
            self.protocol.initialize_handshake(self.stream, file_name, DOWNLOAD)

            self.logger.info("Client up")
            self.logger.info("Connection established")

            start_time = time.time()
            bytes_transferred = 0
            total_packets_sent = 0

            with open(save_path + file_name, "wb") as file:
                while True:
                    try:
                        packet = self.protocol.recv_packet(self.stream)
                        if packet.is_fin():
                            break
                        file.write(packet.get_payload())
                        bytes_transferred += len(packet.get_payload())
                        total_packets_sent += 1

                    except MaximumRetriesError as e:
                        os.remove(save_path + file_name)
                        self.logger.info(f"Exception occurred: {e}, incomplete file removed")
                        self.stream.close()
                        self.logger.info("Socket closed, exiting client")
                        exit(ERROR)
                end_time = time.time()
                transfer_time = end_time - start_time
                average_transfer_speed = bytes_transferred / transfer_time / 1024  # KB/s
                self.logger.info(f"Download completed for file: {file_name}. It was saved in {save_path}")
                self.logger.info(f"Total transfer time: {transfer_time: .2f} seconds.")
                self.logger.info(f"Average transfer speed: {average_transfer_speed:.2f} KB/s")
                self.logger.info(f"Total number of packets sent: {total_packets_sent}")

        def verify_size(self, file_name, file_path):
            size = os.path.getsize(os.path.join(file_path, file_name))

            if(size > MAX_SIZE_FILE):
                text = "Max size file error - The limit is ", MAX_SIZE_FILE, " bytes"
                raise MaxSizeFileError(text)
        
        def upload_file(self, file_name, file_path):

            try:
                self.verify_size(file_name, file_path)
            except MaxSizeFileError:
                self.logger.info(f"Max size file error, the limit is {MAX_SIZE_FILE} bytes")
                exit(ERROR)

            if not os.path.isfile(file_path + file_name):
                self.logger.error(f"File {file_path} does not exist")
                return

            self.logger.info("Client up")
            self.logger.info(f"Uploading {file_path} to Server with file name {file_name}")
            self.protocol.initialize_handshake(self.stream, file_name, UPLOAD)
            self.logger.info("Connection established")

            start_time = time.time()
            bytes_transferred = 0
            total_packets_sent = 0

            file_size = os.stat(file_path)
            self.logger.info(f"File size to be sent: {file_size.st_size} bytes")
            

            with open(file_path + file_name, "rb") as file:
                data = file.read(PAYLOAD_SIZE)
                while data:
                    packet = Packet.new_reg_packet(data, UPLOAD)
                    self.protocol.send_packet(packet, self.stream)
                    data = file.read(PAYLOAD_SIZE)
                    bytes_transferred += len(packet.get_payload())
                    total_packets_sent += 1
                fin_packet = Packet.new_fin_packet()
                try:
                    self.protocol.send_packet(fin_packet, self.stream)
                except MaximumRetriesError as e:
                    self.logger.error(f"Exception occurred: {e}")

            end_time = time.time()
            transfer_time = end_time - start_time
            average_transfer_speed = bytes_transferred / transfer_time / 1024  # en KB/s
            self.logger.info(f"Upload completed for file: {file_name}")
            self.logger.info(f"Total transfer time: {transfer_time: .2f} seconds.")
            self.logger.info(f"Average transfer speed: {average_transfer_speed:.2f} KB/s")
            self.logger.info(f"Total number of packets sent: {total_packets_sent}")
