import struct
from Messages import pieceMessage
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import BLOCK_SIZE, Piece
import bitstring
import random
import hashlib
tracker = Tracker("torrents/torrent1.torrent")
# tracker.peers = {('38.91.112.26', 48392), ('88.15.7.101', 17165), ('31.0.56.88', 44819), ('188.27.128.217', 50165), ('31.0.33.27', 43619), ('37.19.198.94', 62414), ('176.205.102.125', 8000), ('108.191.191.222', 10213), ('0.0.0.0', 65535), ('81.33.249.181', 35308), ('83.32.14.185', 37211), ('121.98.62.85', 31264), ('178.238.172.120', 19446), ('109.166.137.125', 25028), ('138.117.178.219', 60024), ('79.119.253.220', 38972), ('104.221.97.24', 48392), ('37.187.89.189', 55013), ('38.7.250.73', 7746), ('212.251.172.15', 59389), ('86.99.228.99', 62056), ('68.235.43.86', 36873), ('31.0.0.0', 0), ('186.96.210.98', 36048), ('84.50.198.254', 60075), ('188.83.68.14', 46946), ('189.183.27.11', 38423), ('102.65.65.158', 57801), ('243.122.67.198', 48392), ('92.191.68.106', 21275), ('0.0.13.221', 48392), ('66.115.142.185', 31698), ('41.222.248.111', 16909), ('83.51.44.250', 9080), ('115.134.109.189', 34445), ('45.132.115.122', 53021), ('179.6.43.42', 21708), ('187.246.171.5', 53593), ('181.231.42.196', 51413), ('81.182.21.156', 12627), ('37.133.240.208', 62786), ('32.1.8.248', 5677), ('91.214.254.120', 8000), ('110.50.85.144', 21336), ('109.97.116.99', 26670), ('68.235.43.86', 41783), ('105.244.64.116', 12233), ('112.205.224.224', 49425), ('0.0.0.0', 0), ('68.32.109.105', 29555), ('46.6.7.30', 50954)}
tracker.get_peer_list()
p = PeerManager(tracker)
p.connect()
# print(tracker.torrent_obj.total_length)
# print(len(p.piece_manager.pieces))

f = open("ab.bin", "wb")
# convert to while
for i, piece in enumerate(p.piece_manager.pieces):
    print("--------------------")
    print(piece.piece_index)
    peers = p.get_peers_having_piece(piece)
    if peers == []:
        continue
    re = p.request_pieceByteString(piece)
    check = 0
    complete_piece = b''
    for j, r in enumerate(re):
        print("-------")
        for peer in peers:
            if peer.sock:
                try:
                    peer.sock.send(r)
                except:
                    continue 
                data = p.read_piece_response(peer.sock, struct.unpack(">IBIII", r)[4])
                if data == None:
                    continue
                # piece.blocks[j].data = data
                # check += 1
                print(j, len(data))
                complete_piece += data
                break
    print(piece.piece_sha1, hashlib.sha1(complete_piece).digest())
    if piece.piece_sha1 == hashlib.sha1(complete_piece).digest(): 
        f.seek(0, 2)
        f.write(complete_piece)         
    print()
    
f.close()
#write into_file




