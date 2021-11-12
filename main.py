from socket import socket
import struct
from Messages import Bitfield, keep_alive, pieceMessage
from peer import Peer
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import BLOCK_SIZE, Piece
import socket
import random
import threading
import time


class Bittorrent:
    def __init__(self) -> None:
        pass
    def start_downloading(self, torrent):
        throttleSendRateBytes = 0
        tracker = Tracker(torrent)
        tracker.get_peer_list()
        time.sleep(7)
        tracker.exitAllThreads()
        p = PeerManager(tracker)
        print(tracker.torrent_obj.total_length)
        p.connect()
        time.sleep(5)
        minHeap = p.piece_manager.getRarestPieceMinHeap(p.connected_peers)
        
        file_thread = threading.Thread(target=p.piece_manager.write_into_file)
        file_thread.start()

        percentage_thread = threading.Thread(target=p.piece_manager.percentage, args = (p.connected_peers, ))
        percentage_thread.start()

        while p.piece_manager.all_piece_complete() == False:
            index = None
            for x in minHeap:
                index = x[0]
                
                # piece = p.piece_manager.getRandomPiece()
                piece:Piece = p.piece_manager.pieces[index]
                peers:Peer = p.get_peer_having_piece(piece)
                if not peers:                    
                    print("No Peers.. Connecting to peer again...")
                    time.sleep(4)
                    continue
                peer:Peer = random.choice(peers)
                if peer.peer_choking == 1:
                    continue
                for block_index, block in enumerate(piece.blocks):
                    # if len(block.data) != 0:
                    #     continue
                    # block_index = piece.get_empty_block()
                    # if piece.blocks[block_index].last_requested:
                    #     curr = time.time()
                    #     last = piece.blocks[block_index].last_requested
                    #     if curr - last < 5:
                    #         continu    
                    try:
                        request_block = p.request_blockByteString(piece, block_index, piece.blocks[block_index])
                        if time.time() - peer.last_transmission > 60:
                            request_block += keep_alive.byteStringForKeepAlive()
                            peer.last_transmission = time.time()
                        # if throttleSendRateBytes > 128:
                        #     print("Throttling Sending Rate")
                        #     time.sleep(0.05)
                        #     throttleSendRateBytes = 0
                        # throttleSendRateBytes += len(request_block)
                        peer.sock.send(request_block)
                        peer.last_transmission = time.time()
                        # time.sleep(0.05)
                        # print(f"REQUESTING BLOCK FROM {peer.ip_port} with PIECE INDEX : {piece.piece_index} and BLOCK INDEX : {block_index} from {peer.ip_port}")
                        piece.blocks[block_index].last_requested = time.time()
                    except Exception as e:
                        p.connected_peers.remove(peer)
                        print(f"{e} for {peer.ip_port}")
                        time.sleep(1)
        print("Torrent Complete")
        p.exitPeerThreads()
        file_thread.join()
        
d = Bittorrent()
d.start_downloading("torrents/torrent4.torrent")