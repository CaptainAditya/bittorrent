import struct
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import BLOCK_SIZE, Piece
import random
tracker = Tracker("torrents/torrent2.torrent")
tracker.get_peer_list()
p = PeerManager(tracker)
p.connect()
print(tracker.torrent_obj.total_length)
for i, piece in enumerate(p.piece_manager.pieces):
    print(piece.piece_index)
    peers = p.get_peers_having_piece(piece)
    if peers == []:
        continue
    re = p.request_pieceByteString(piece)
    check = 0
    for j, r in enumerate(re):
        for peer in peers:
            if peer.sock:
                try:
                    peer.sock.send(r)
                except:
                    continue 
                data = p.read_piece_response(peer.sock, struct.unpack(">IBIII", r)[4])
                if data == None:
                    continue
                piece.blocks[j].data = data
                check += 1
                break
    if check != piece.number_of_blocks:
        print(f"Piece{i} Incomplete")
    print()


#write into_file

