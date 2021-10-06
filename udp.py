import struct, random
from sys import int_info
class udpTrackerConnecting:
    def __init__(self):
        self.connection_id = struct.pack('>Q', 0x41727101980)
        self.action = struct.pack('>I', 0)
        trans_id = random.randint(0, 1000)
        self.transaction_id = struct.pack('>I', trans_id)
    def bytestringForConnecting(self):
        return self.connection_id + self.action + self.transaction_id
    def parse_response(self, data):
        format_to_unpack = 'IIQ'
        tracker_connection_response = struct.unpack(format_to_unpack, data)
        self.server_connection_id = tracker_connection_response[2]
class udpTrackerAnnouncing:
    def __init__(self, conn_id, info_hash, peer_id, left, port):
        self.connection_id = struct.pack('>Q', conn_id)
        self.action = struct.pack('>I', 1)
        trans_id = random.randint(0, 1000)
        self.transaction_id = struct.pack('>I', trans_id)
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.downloaded = struct.pack('>Q', 0)
        self.left = struct.pack('>Q', left)
        self.uploaded = struct.pack('>Q', 0)
        self.event = struct.pack('>I', 0)
        self.ip = struct.pack('>I', 0)
        self.key = struct.pack('>I', 0)
        self.num_want = struct.pack('>i', -1)
        self.port = struct.pack('>H', port)
    def byteStringAnnounce(self):
        return (self.connection_id + self.action + self.transaction_id + self.info_hash + self.peer_id 
                + self.downloaded + self.left + self.uploaded + self.event + self.ip + self.key + self.num_want + self.port)
    
    def parse_response(self, response):
        server_action = struct.unpack('>I', response[:4])
        transaction_id = struct.unpack('>I', response[4 : 8])
        interval = struct.unpack('>I', response[8:12])
        leechers = struct.unpack('>I' ,response[12:16])
        seeders = struct.unpack('>I', response[16 : 20])
        info = list([str(x) for x in response[20:]])
        ip_port = []
        i = 0
        while i < len(info) - len(info) % 6:
            ip = ".".join(info[i : i + 4])
            port = int(info[i + 4]) * 256 + int(info[i + 5])
            ip_port.append((ip, port))
            i += 6
        return ip_port
