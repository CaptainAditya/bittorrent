from peer import Handshake, Peer
from tracker import Tracker
from peer import Peer
import threading
import socket
from Messages import interested

# p = {'http://p4p.arenabg.com:1337/announce': [('31.14.145.38', 55988), ('46.33.212.186', 29385), ('81.92.202.30', 35102), ('114.108.224.71', 24243), ('112.201.103.167', 14742), ('112.200.170.12', 55824), ('112.200.111.120', 20885), ('112.200.26.58', 49160), ('110.93.205.130', 44097), ('105.244.20.250', 36491), ('105.235.240.13', 44153), ('105.226.99.203', 46271), ('105.209.173.141', 24645), ('105.163.1.132', 13967), ('103.104.218.9', 40723), ('103.25.242.101', 8348), ('102.222.181.67', 41249), ('102.220.105.115', 46639), ('102.66.136.39', 49160), ('102.22.202.22', 12131), ('94.204.110.157', 23402), ('94.4.243.102', 14967), ('92.99.209.132', 16917), ('91.132.138.250', 52830), ('87.116.191.105', 51413), ('86.98.44.164', 41517), ('85.98.53.22', 48882), ('84.220.63.26', 23224), ('82.178.63.186', 21315), ('79.126.97.128', 48882), ('77.247.181.216', 1), ('67.175.191.111', 60944), ('58.179.207.118', 45610), ('49.207.194.108', 16817), ('49.145.134.123', 31575), ('49.37.213.11', 60638), ('46.166.191.18', 16543), ('45.132.115.135', 58208), ('45.131.193.24', 64707), ('41.216.201.204', 11962), ('41.204.187.5', 54672), ('41.198.132.90', 16984), ('41.174.42.113', 19476), ('41.161.60.210', 38408), ('41.80.112.213', 14603), ('41.58.237.165', 38591), ('37.208.187.213', 49139), ('27.147.207.229', 35074), ('24.156.189.22', 63637), ('5.79.77.10', 47623)]}
# for key, value in t.peers.items():
#     for ip_port in value:
#         p = peer(ip_port)
#         p.connect_to_peer()

class PeerManager:
    def __init__(self, tracker_obj):
        self.tracker_obj = tracker_obj
    def connect(self):
        for peer in self.tracker_obj.peers:
            peer_obj = Peer(peer)
            sock = peer_obj.connect_to_peer()
            if sock:
                handshake = Handshake(self.tracker_obj.torrent_obj.peer_id, self.tracker_obj.torrent_obj.info_hash)
                sock.send(handshake.getHandshakeBytes())
                try:
                    data = sock.recv(8192)
                    #check peer_id
                    print("Hand Shake received")
                    threading.Thread(target = self.MultiThreadedDownload, args = (peer_obj, sock, )).start()
                except Exception as e:
                    print(f"HandShake Problem for {peer_obj.ip_port}")
    def MultiThreadedDownload(self, peer, sock):
        interested_message = interested()
        sock.send(interested_message.byteStringForInterested())
        sock.timeout(7)
        try:
            data = sock.recv(4096)
        except:
            print(peer.ip_port)
            print("timeout")

        print(data)