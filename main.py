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

tracker = Tracker("torrents/torrent1.torrent")
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
    print(f"REQUESTING BLOCK FROM {peer.ip_port} with piece index {piece.piece_index} and block index {block_index}")
    try:
        peer.sock.send(request_block)
    except:
        continue
    time.sleep(1)
print("TOrrent COmpleeter")

f = open(tracker.torrent_obj.name, "wb")
for i, piece in enumerate(p.piece_manager.pieces):
    complete_piece = p.piece_manager.merge_blocks(i)
    print(hashlib.sha1(complete_piece).digest(), piece.piece_sha1)
    for block in piece.blocks:
        f.write(block.data)
f.close()