from socket import socket
from Messages import keep_alive
from peer import Peer
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import Piece
import socket
import random
import threading
import time
import os, sys

class Bittorrent:
    def __init__(self) -> None:
        pass
    def startDownloading(self, torrent, path):
        # throttleSendRateBytes = 0
        tracker = Tracker(torrent, path)
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

        # percentage_thread = threading.Thread(target=p.piece_manager.percentage, args = (p.connected_peers, ))
        # percentage_thread.start()

        while p.piece_manager.all_piece_complete() == False:
            for x in minHeap:
                index = x[0]
                
                # piece = p.piece_manager.getRandomPiece()
                piece:Piece = p.piece_manager.pieces[index]
                if piece.is_complete():
                    continue
                peers:Peer = p.get_peer_having_piece(piece)
                if not peers:                    
                    print("No Peers.. Connecting to peer again...")
                    time.sleep(10)
                    continue
                peer:Peer = random.choice(peers)
                if peer.peer_choking == 1:
                    continue
                for block_index, block in enumerate(piece.blocks): 
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
                        
                        # print(f"REQUESTING BLOCK FROM {peer.ip_port} with PIECE INDEX : {piece.piece_index} and BLOCK INDEX : {block_index} from {peer.ip_port}")
                        piece.blocks[block_index].last_requested = time.time()
                    except Exception as e:
                        if peer in p.connected_peers:
                            p.connected_peers.remove(peer)
                        print(f"{e} for {peer.ip_port}")
                        time.sleep(1)
                p.piece_manager.printProgressBar(p.piece_manager.downloadBlocks(), p.piece_manager.totalBlocks, f"Kbps {p.findRate()} Peers {len(p.connected_peers)}", f"Completed {p.piece_manager.piecesDownloaded()}/{len(p.piece_manager.pieces)}")
                
        print("Torrent Complete")
        print(tracker.torrent_obj.total_length)
        p.exitPeerThreads()
        file_thread.join()

        
torrent = sys.argv[1]
path = sys.argv[2]
b = Bittorrent()
b.startDownloading(torrent, path)