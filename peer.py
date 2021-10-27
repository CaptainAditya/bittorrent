import socket
import struct
from ipaddress import ip_address, IPv4Address
import bitstring
def validIPAddress(IP: str) -> str:
    try:
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"

class Peer:
    def __init__(self, ip_port, number_of_pieces):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)          
        self.bit_field = bitstring.BitArray(number_of_pieces)
        self.ip_port = ip_port
        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0
    def connect_to_peer(self):
        if validIPAddress(self.ip_port[0]) == "IPv6":
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.ip_port = (self.ip_port[0], self.ip_port[1], 0, 0)
        print("Attempting connection to ", self.ip_port)
        self.sock.settimeout(12)
        try:
            self.sock.connect(self.ip_port)
            print("Success")
            return self.sock
        except Exception as e:
            return None

class Handshake():
    def __init__(self, peer_id, info_hash):
        pstr = b"BitTorrent protocol"
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.pstr = pstr
        self.pstrlen = len(pstr)
        self.reserved = b'x\00' * 8
        self.handshake = struct.pack(">B{}s8s20s20s".format(self.pstrlen),
                            self.pstrlen,
                            self.pstr,
                            self.reserved,
                            self.info_hash,
                            self.peer_id)
    def getHandshakeBytes(self):
        return self.handshake
    

    



            
