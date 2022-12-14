from math import pi
from BlockandPiece import BLOCK_SIZE, Block
from peer import Handshake, Peer
from tracker import Tracker
from peer import Peer
import threading
import socket
from Messages import *
from PieceInfo import PieceInfo
import errno
import socket
import time
MAX_CONNECTED_PEER = 8
class PeerManager:
    def __init__(self, tracker_obj):
        self.tracker_obj = tracker_obj
        self.piece_manager = PieceInfo(self.tracker_obj.torrent_obj)
        self.number_of_pieces = self.piece_manager.number_of_pieces
        self.peers = []
        self.threads = {}
        self.connected_peers = []
    def exitPeerThreads(self):
        for peer, thread in self.threads.items():
            thread.join()
    def connect(self):
        threads = []
        for peer in self.tracker_obj.peers:
            peer_obj = Peer(peer, self.number_of_pieces)
            p = threading.Thread(target=self.MultiThreadedConnection, args=(peer_obj, )) 
            p.start()
    def read_continously_from_sock(self, sock, peer : Peer):  
        if len(self.connected_peers) < MAX_CONNECTED_PEER:
            self.connected_peers.append(peer)  
        else: return
        try:
            while True:
                length = sock.recv(4)
                # if len(length) < 4:
                #     break
                length_u, = struct.unpack(">I", length)
                if length_u == 0:
                    continue
                if length_u == 1:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID_u == 0:
                        print(f"{peer.ip_port} choked")
                        peer.peer_choking = 1
                    elif message_ID_u == 1:
                        print(f"{peer.ip_port} unchoked")
                        peer.peer_choking = 0
                    elif message_ID_u == 2:
                        peer.peer_interested = 1
                    elif message_ID_u == 3:
                        peer.peer_interested = 0
                elif length_u == 5:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID_u == 4:
                        piece_i = sock.recv(4)
                        piece_info = have.parse_response(length + message_ID + piece_i)
                        peer.bit_field[piece_info.piece_index] = True
                        print(f"{peer.ip_port} have message recieved")

                else:
                    message_ID = sock.recv(1)
                    message_ID_u, = struct.unpack(">B", message_ID)
                    if message_ID_u == 5:
                        raw_bytes = PeerManager._read_piece_data(sock, length_u - 1, peer)
                        bitField_obj = Bitfield.parse_response(length + message_ID + raw_bytes)
                        print(f"bitfield for peer with {peer.ip_port} has length {len(peer.bit_field)}")
                        print(f"bitfield object has {len(bitField_obj.bitfield)}")
                        if length_u - 1 == len(raw_bytes):
                            peer.bit_field = bitField_obj.bitfield
                        else:
                            for i, x in enumerate(bitField_obj.bitfield[ : len(peer.bit_field)]):
                                peer.bit_field[i] = x
                        print(f"{peer.ip_port} bitfield done")

                    elif message_ID_u == 7:
                        index_begin = sock.recv(8)
                        raw_bytes = PeerManager._read_piece_data(sock, length_u - 9, peer)
                        piece_obj = pieceMessage.parse_response(length + message_ID + index_begin + raw_bytes)
                        piece_index, block_length, block_offset, block = piece_obj
                        block_index = block_offset // BLOCK_SIZE
                        self.piece_manager.pieces[piece_index].blocks[block_index].data = block
                        self.piece_manager.pieces[piece_index].blocks[block_index].status = 1        
                        # print(f"RECIEVED PIECE FROM {peer.ip_port} WITH PIECE INDEX : {piece_index} BLOCK INDEX : {block_index}")
               
        except Exception as e:
            if peer in self.connected_peers:
                self.connected_peers.remove(peer)
        
    @staticmethod
    def _read_piece_data(sock, length, peer):
        data = b''
        required = length
        
        while True:
            try:
                start = time.time()
                buff = sock.recv(required)
                end = time.time()
                peer.rate = len(buff) // 125
                peer.rate = peer.rate // (end - start)
                if len(buff) <= 0:
                    break
                data += buff
                required = length - len(data)
                if len(data) == length:
                    break
            except socket.error as e:
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    # logging.debug("Wrong errno {}".format(err))
                    pass
                break
            except Exception as e:
                # logging.exception("Recv failed")
                break
        if len(data) <= 0:
            return None
        return data
        
    def MultiThreadedConnection(self, peer:Peer):
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
                print(f"HandShake Problem for {peer.ip_port} {e}")
                return
            self.peers.append(peer)
            interested_message = interested()
            peer.last_transmission = time.time()
            sock.send(interested_message.byteStringForInterested())
            peer.am_interested = 1
            sock.settimeout(None)
            t = threading.Thread(target=self.read_continously_from_sock, args = (sock, peer, ))
            self.threads[peer] = t
            t.start()
        return

    def get_peer_having_piece(self, piece : Piece):
        index = piece.piece_index
        peers_having_piece = []
        for peers in self.connected_peers:
            if peers.bit_field[index] == True:
                peers_having_piece.append(peers)
        return peers_having_piece
    def request_blockByteString(self, piece, block_index, block):
        request_obj = request(piece.piece_index, block_index * BLOCK_SIZE, block.block_size)
        return request_obj.byteStringForRequest()

    def findRate(self):
        sum = 0
        n = 0
        for peer in self.connected_peers:
            if peer.rate:
                sum += peer.rate
                n += 1
        try:
            rate = sum // n
            return rate
        except:
            return 0

    def showRatePeers(self):
        rates = []
        for peer in self.connected_peers:
            if peer.rate:
                rates.append((peer, peer.rate))
        return rates