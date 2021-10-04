import struct, random
from socket import socket
class udpTracker:
    def __init__(self, udp_tracker):
        connection_id = struct.pack('>Q', 0x41727101980)
        action = struct.pack('I', 0)
        transaction_id = struct.pack('I', random.randint(0,1000))
        