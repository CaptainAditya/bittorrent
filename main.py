from socket import socket
import struct
from Messages import pieceMessage
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import BLOCK_SIZE, Piece
import bitstring
import socket
import random
import hashlib
import threading
import time
import errno

tracker = Tracker("torrents/friends.torrent")
tracker.get_peer_list()
p = PeerManager(tracker)
print(tracker.torrent_obj.total_length)
p.connect()

while p.piece_manager.all_piece_complete() == False:
    
    piece = p.piece_manager.getRandomPiece()
    peers = p.get_peer_having_piece(piece)
    if not peers:
        continue
    peer = random.choice(peers)
    block_index = piece.get_empty_block()
    if block_index == None:
        continue
    request_block = p.request_blockByteString(piece , block_index, piece.blocks[block_index])
    print(f"REQUESTING BLOCK FROM {peer.ip_port} with PIECE INDEX : {piece.piece_index} and BLOCK INDEX : {block_index}")
    try:
        peer.sock.send(request_block)
    except:
        continue
    time.sleep(1)
    p.piece_manager.percentage()
print("TOrrent COmpleeter")

