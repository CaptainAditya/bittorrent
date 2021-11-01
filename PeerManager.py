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
import random
import socket

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
                if len(length) < 4:
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
    @staticmethod
    def _read_from_socket(sock:socket.socket, piece:Piece, block_index, block_obj : Block):
        data = b''
        sock.settimeout(10)
        while True:
            try:
                buff = sock.recv(4096)
                if len(data + buff) > 16400:
                    break
                if len(buff) <= 0:
                    break
                data += buff
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
            return
        print(piece.piece_index, block_index, len(data))
        piece.blocks[block_index].status = 1
        piece.blocks[block_index].data = data
        
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
            sock.settimeout(7)
            self.read_continously_from_sock(sock, peer)
            print(peer.bit_field)
        return

    def get_peer_having_piece(self, piece):
        index = piece.piece_index
        peers_having_piece = []
        for peers in self.peers:
            if peers.bit_field[index] == True:
                peers_having_piece.append(peers)
        return random.choice(peers_having_piece) if peers_having_piece else None
            
    def request_blockByteString(self, piece, block_index, block):
        request_obj = request(piece.piece_index, block_index * BLOCK_SIZE, block.block_size)
        return request_obj.byteStringForRequest()

