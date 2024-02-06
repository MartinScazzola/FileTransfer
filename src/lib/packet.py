from lib.constants import *


class Packet:

    def __init__(
        self,
        sequence_number,
        ack_number,    
        ack,
        syn,
        fin,
        download,
        payload,
    ):
        self.sequence_number = sequence_number
        self.ack_number = ack_number
        self.ack = ack   
        self.syn = syn
        self.fin = fin
        self.download = download
        self.payload = payload


    def to_bytes(self):

        flags = 0b0000_0000
        if self.ack:
            flags |= 0b1000_0000
        if self.syn:
            flags |= 0b0100_0000
        if self.fin:
            flags |= 0b0010_0000
        if self.download:
            flags |= 0b0001_0000

        packet = (
            self.sequence_number.to_bytes(4, "big")
            + self.ack_number.to_bytes(4, "big")
            + flags.to_bytes(1, "big")
            + self.payload
        )
        return packet

    def new_reg_packet(payload, operation):
        return Packet(
            sequence_number=0,
            ack_number=0,
            ack=False,
            syn=False,
            fin=False,
            download= (operation),
            payload=payload
        )

    def new_ack_packet(sequence_number, ack_number, operation):
        return Packet(
            sequence_number=sequence_number,
            ack_number=ack_number,
            ack=True,
            syn=False,
            fin=False,
            download=operation,
            payload=bytes(),
        )


    def new_syn_packet(sequence_number, ack_number, filename, is_download):
        return Packet(
            sequence_number=sequence_number,
            ack_number=ack_number,
            ack=False,
            syn=True,
            fin=False,
            download=is_download,
            payload=bytes() 
            if filename is None 
            else len(filename).to_bytes(1, byteorder='big') + filename.encode('utf-8'),
        )
    
    def new_fin_packet():
        return Packet(
            sequence_number=0,
            ack_number=0,
            ack=False,
            syn=False,
            fin=True,
            download=False,
            payload=bytes(),
        )


    def from_bytes(bytes):
        sequence_number = int.from_bytes(bytes[0:4], "big")
        ack_number = int.from_bytes(bytes[4:8], "big")
        flags= bytes[8]
        payload = bytes[9:]
        
        ack = False
        syn = False
        fin = False
        download = False

        if (flags & 0b1000_0000) >> 7:
            ack = True
        if (flags & 0b0100_0000) >> 6:
            syn = True
        if (flags & 0b0010_0000) >> 5:
            fin = True
        if (flags & 0b0001_0000) >> 4:
            download = True

        return Packet(
            sequence_number=sequence_number,
            ack_number=ack_number,
            ack=ack,
            syn=syn,
            fin=fin,
            download=download,
            payload=payload,
        )

    def get_payload(self):
        return self.payload

    def is_ack(self):
        return self.ack
    
    def is_syn(self):
        return self.syn

    def is_fin(self):
        return self.fin
    
    def is_download(self):
        return self.download

    def __str__(self):
        return f"sequence_number: {self.sequence_number},  is_ack: {self.ack}, payload_len: {len(self.payload)}, ack_number : {self.ack_number}"