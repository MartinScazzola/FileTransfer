import queue
from lib.constants import *
from lib.packet import Packet
from socket import *

from lib.protocol import Protocol


class SelectiveRepeat(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.packet_window = {}
        self.recv_buffer = {}

    
    def send_packet(self, packet, stream):
        
        packet.sequence_number = self.sequence_number
        packet.ack_number = self.ack_number

        
        if len(self.packet_window) <  WINDOW_SIZE:
            stream.send_to(packet.to_bytes(), self.address)
            self.logger.debug(f"Packet sent as ({packet})")
            self.packet_window[packet.sequence_number] = packet
            self.sequence_number += 1

        else:
            status = self._wait_ack(stream)
            if status==OK:
                stream.send_to(packet.to_bytes(), self.address)
                self.logger.debug(f"Packet sent as ({packet})")
                self.packet_window[packet.sequence_number] = packet
                self.sequence_number += 1
        if packet.is_fin():
            self._wait_last_packets(stream)

        

    def _wait_ack(self, stream):
        retries = 0
        while retries < MAX_RETRANSMITS:
            repeated_ack = 0
            while repeated_ack < MAX_REPEATED_ACKS:   
                try:
                    ack_packet = stream.receive()
                    self.logger.debug(f"Received packet as {ack_packet}")

                    if ack_packet.is_fin():
                        new_dic = {} 
                        self.packet_window = new_dic
                        return OK

                    if not ack_packet.is_ack():
                        self.logger.debug("Unexpected packet")
                        continue
                    
                    if ack_packet.ack_number - 1 in self.packet_window:
                        self.packet_window.pop(ack_packet.ack_number - 1)

                        new_dic = {} 
                        for sec in self.packet_window.keys():
                             if sec >= ack_packet.ack_number:
                                  new_dic[sec] = self.packet_window[sec]
                        self.packet_window = new_dic

                        return OK
                    repeated_ack += 1
                except (timeout, queue.Empty):
                    self.logger.debug("Timeout event occurred on send. Retrying...")
                    repeated_ack += 1
            retransmit_packet = self.packet_window.get(min(self.packet_window.keys()))
        
            stream.send_to(retransmit_packet.to_bytes(), self.address)
            self.logger.debug(f"Retransmitted packet sent as ({retransmit_packet})")
            retries+=1
        
           
        return FIN

    def recv_packet(self, stream):
        receive_count = 0
        if (self.ack_number in self.recv_buffer):
                        
                        packet =  self.recv_buffer[self.ack_number]
                        del self.recv_buffer[self.ack_number]
                        self.ack_number+= 1
                        ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                        stream.send_to(ack.to_bytes(), self.address)
                        return packet
        
        while receive_count < RETRIES:
            try:
                packet = stream.receive()
                self.logger.debug(f"Received packet as {packet}")
                if packet.sequence_number > self.ack_number:
                    self.logger.debug("Received packet is not ack or ack number is not correct")
                    self.recv_buffer[packet.sequence_number] = packet
                    
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as ({ack})")
                elif packet.sequence_number == self.ack_number:
                    self.ack_number = packet.sequence_number + 1
                   
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as ({ack})")
                    return packet
            except (timeout, queue.Empty):
                ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                self.logger.debug(f"Ask for retransmission for ({self.ack_number})")
                stream.send_to(ack.to_bytes(), self.address)
                self.logger.debug("Timeout event occurred on receive. Retrying...")
            receive_count+=1
        
    def _wait_last_packets(self, stream):
            retries = 0
            while(len(self.packet_window) > 0 ):
                if(retries >= WINDOW_SIZE):
                    self.logger.debug(f"Retransmission limit reached")
                    return
                self.logger.debug(f"Waiting last packets")
                self._wait_ack(stream)
                retries +=1
        
  