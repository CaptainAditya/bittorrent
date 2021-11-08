from socket import socket
import struct
from Messages import pieceMessage
from peer import Peer
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
from heapq import heapify, heappush, heappop


tracker = Tracker("torrents/friends.torrent")
tracker.get_peer_list()
time.sleep(7)
tracker.exitAllThreads()
p = PeerManager(tracker)
print(tracker.torrent_obj.total_length)
p.connect()
time.sleep(10)
minHeap = p.piece_manager.getRarestPieceMinHeap(p.connected_peers)
print(minHeap)
while p.piece_manager.all_piece_complete() == False:
    index = None
    for x in minHeap:
        index = x[0]
        if p.piece_manager.pieces[index].is_complete() == False:
            break
    
    # piece = p.piece_manager.getRandomPiece()
    piece:Piece = p.piece_manager.pieces[index]
    peers:Peer = p.get_peer_having_piece(piece)
    if not peers:
        continue

    peer = random.choice(peers)
    block_index = piece.get_empty_block()
    # if piece.blocks[block_index].last_requested:
    #     curr = time.time()
    #     last = piece.blocks[block_index].last_requested
    #     if curr - last < 5:
    #         continue

    request_block = p.request_blockByteString(piece , block_index, piece.blocks[block_index])
    print(f"REQUESTING BLOCK FROM {peer.ip_port} with PIECE INDEX : {piece.piece_index} and BLOCK INDEX : {block_index}")
    piece.blocks[block_index].last_requested = time.time()
    try:
        peer.sock.send(request_block)
    except:
        continue
    time.sleep(1)
    p.piece_manager.percentage()
print("Torrent Complete")

p.piece_manager.write_into_file()
