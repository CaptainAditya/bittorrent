from math import pi
from BlockandPiece import BLOCK_SIZE
from peer import Handshake, Peer
from tracker import Tracker
from peer import Peer
import threading
import socket
from Messages import *
from PieceInfo import PieceInfo
import errno
import socket
# p = {'http://p4p.arenabg.com:1337/announce': [('31.14.145.38', 55988), ('46.33.212.186', 29385), ('81.92.202.30', 35102), ('114.108.224.71', 24243), ('112.201.103.167', 14742), ('112.200.170.12', 55824), ('112.200.111.120', 20885), ('112.200.26.58', 49160), ('110.93.205.130', 44097), ('105.244.20.250', 36491), ('105.235.240.13', 44153), ('105.226.99.203', 46271), ('105.209.173.141', 24645), ('105.163.1.132', 13967), ('103.104.218.9', 40723), ('103.25.242.101', 8348), ('102.222.181.67', 41249), ('102.220.105.115', 46639), ('102.66.136.39', 49160), ('102.22.202.22', 12131), ('94.204.110.157', 23402), ('94.4.243.102', 14967), ('92.99.209.132', 16917), ('91.132.138.250', 52830), ('87.116.191.105', 51413), ('86.98.44.164', 41517), ('85.98.53.22', 48882), ('84.220.63.26', 23224), ('82.178.63.186', 21315), ('79.126.97.128', 48882), ('77.247.181.216', 1), ('67.175.191.111', 60944), ('58.179.207.118', 45610), ('49.207.194.108', 16817), ('49.145.134.123', 31575), ('49.37.213.11', 60638), ('46.166.191.18', 16543), ('45.132.115.135', 58208), ('45.131.193.24', 64707), ('41.216.201.204', 11962), ('41.204.187.5', 54672), ('41.198.132.90', 16984), ('41.174.42.113', 19476), ('41.161.60.210', 38408), ('41.80.112.213', 14603), ('41.58.237.165', 38591), ('37.208.187.213', 49139), ('27.147.207.229', 35074), ('24.156.189.22', 63637), ('5.79.77.10', 47623)]}
# for key, value in t.peers.items():
#     for ip_port in value:
#         p = peer(ip_port)
#         p.connect_to_peer()

class PeerManager:
    def __init__(self, tracker_obj):
        self.tracker_obj = tracker_obj
        self.piece_manager = PieceInfo(self.tracker_obj.torrent_obj)
        self.number_of_pieces = self.piece_manager.number_of_pieces
        self.peers = []
    
    def connect(self):
        threads = []
        for peer in self.tracker_obj.peers:
            peer_obj = Peer(peer, self.number_of_pieces)
            t = threading.Thread(target = self.MultiThreadedConnection, args = (peer_obj,))
            t.start()
            threads.append(t)
        for process in threads:
            process.join()
        
            # sock = peer_obj.connect_to_peer()
            # if sock:
            #     handshake = Handshake(self.tracker_obj.torrent_obj.peer_id, self.tracker_obj.torrent_obj.info_hash)
            #     sock.send(handshake.getHandshakeBytes())
            #     try:
            #         data = sock.recv(8192)
            #         #check peer_id
            #         print("Hand Shake received")
            #         threading.Thread(target = self.MultiThreadedDownload, args = (peer_obj, sock, )).start()
            #     except Exception as e:
            #         print(f"HandShake Problem for {peer_obj.ip_port}")
    def read_continously_from_sock(self, sock, peer):
        while True:
            try:
                length = sock.recv(4)
                print(length)
                if len(length) <= 0:
                    break
                length_u, = struct.unpack(">I", length)
                if length_u == 1:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID == 0:
                        print(f"{peer.ip_port} choked")
                        peer.peer_chocking = 1
                    elif message_ID == 1:
                        peer.peer_chocking = 0
                    elif message_ID == 2:
                        peer.peer_interested = 1
                    elif message_ID == 3:
                        peer.peer_interested = 0
                elif length_u == 5:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID_u == 4:
                        piece_i = sock.recv(4)
                        piece_info = have.parse_response(length + message_ID + piece_i)
                        peer.bit_field[piece_info.piece_index] = True
                else:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID_u == 5:
                        raw_bytes = sock.recv(length_u - 1)
                        bitField_obj = Bitfield.parse_response(length + message_ID + raw_bytes)
                        if length_u - 1 == len(raw_bytes):
                            peer.bit_field = bitField_obj.bitfield
                        else:
                            for i, x in enumerate(bitField_obj.bitfield):
                                peer.bit_field[i] = x
            except socket.error as e:
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    pass
                break
            except Exception:
                break

    def read_piece_response(self, sock : socket.socket, length):
        res = b''
        res = sock.recv(length)
        l = len(res)
        sock.settimeout(2)
        if l < length:
            while len(res) <= length:
                try:
                    req = length - len(res)
                    if req == 0:
                        return res
                    print(f"Required : {req}")
                    data = sock.recv(req)
                    res += data
                except socket.timeout:
                    return None
                except:
                    return None
        return res
    def MultiThreadedConnection(self, peer):
        sock = peer.connect_to_peer()
        if sock != None:
            handshake = Handshake(self.tracker_obj.torrent_obj.peer_id, self.tracker_obj.torrent_obj.info_hash)
            sock.send(handshake.getHandshakeBytes())
            try:
                data = sock.recv(68)
                if len(data) > 68 or len(data) < 68:
                    return
                #check peer_id
                print("Hand Shake received")
            except Exception as e:
                print(f"HandShake Problem for {peer.ip_port}")
                return
            self.peers.append(peer)
            interested_message = interested()
            sock.send(interested_message.byteStringForInterested())
            sock.settimeout(12)
            self.read_continously_from_sock(sock, peer)
            print(peer.bit_field)
        return
            # ParseMessageFromPeer.parse_response(reply)

    def get_peers_having_piece(self, piece):
        index = piece.piece_index
        peers_having_piece = []
        for peers in self.peers:
            if peers.bit_field[index] == True:
                peers_having_piece.append(peers)
        return peers_having_piece
            
    def request_pieceByteString(self, piece):
        offset = 0
        requests = []
        for block in piece.blocks:
            request_obj = request(piece.piece_index, offset, block.block_size)
            requests.append(request_obj.byteStringForRequest())
            offset += BLOCK_SIZE
        return requests
            



    


    # def checkHaveMessages(self, message):
    #     have_obj = have()
    #     if have_obj.parse_from_response(message) != -1:
            

