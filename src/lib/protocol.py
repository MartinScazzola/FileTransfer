from abc import ABC, abstractmethod
import queue
from lib.constants import *
from lib.packet import Packet
from socket import *



class Protocol(ABC):

    def __init__(self, address, logger):
        self.address = address
        self.sequence_number = 0
        self.ack_number = 0
        self.logger = logger

    
    def initialize_handshake(self, stream, filename, operation):
        retries = 0
        while retries < RETRIES:
            first_syn_send = Packet.new_syn_packet(self.sequence_number, self.ack_number, filename, operation) 
            self.logger.info("Handshake initiated")
            self.logger.info("Sending first syn with sequence number: " + str(self.sequence_number))
            stream.send_to(first_syn_send.to_bytes(), self.address)

            try:
                syn_recv = stream.receive()
            except timeout:
                self.logger.error("Syn response packet was not received")
                retries += 1
                continue

            if not syn_recv.is_syn() or syn_recv.ack_number != self.sequence_number + 1:
                self.logger.error("Received packet is not syn or ack number is not correct")
                retries += 1
                continue

            self.logger.info("Received syn response with sequence number: " + str(syn_recv.sequence_number) + " and ack: " + str(syn_recv.ack_number))

            self.sequence_number += 1
            self.ack_number = syn_recv.sequence_number + 1
            ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, operation)
            stream.send_to(ack.to_bytes(), self.address)
            self.logger.info("Sending ack with sequence number: " + str(self.sequence_number) + " and ack: " + str(self.ack_number))
            return

    
    def response_handshake(self, stream, address, sequence_recv):
        self.logger.info("Received first syn with sequence number: " + str(sequence_recv))
        self.ack_number = sequence_recv + 1
        self.logger.info("Sending second syn with sequence number: " + str(self.sequence_number) + " and ack: " + str(self.ack_number))
        retries = 0
        while retries < SYN_RETRIES:
            syn_send = Packet.new_syn_packet(self.sequence_number, self.ack_number, None, UPLOAD)
            stream.send_to(syn_send.to_bytes(), address)
            try:
                ack = stream.receive()
                if ack.is_ack() and ack.ack_number == self.sequence_number + 1:
                    self.sequence_number += 1
                    return
            except (timeout, queue.Empty):
                self.logger.error("Ack packet was not received")
            retries +=1
        self.sequence_number += 1
       


    @abstractmethod
    def send_packet(self, packet, stream):
        pass

    @abstractmethod
    def recv_packet(self, stream):
        pass