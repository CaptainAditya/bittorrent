import struct
from Messages import pieceMessage
from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
from BlockandPiece import BLOCK_SIZE, Piece
import bitstring
import random
import hashlib
import threading
import time
tracker = Tracker("torrents/torrent1.torrent")
# tracker.peers = {('75.185.30.133', 48392), ('79.131.4.255', 42340), ('90.190.137.53', 60075), ('180.191.195.57', 6881), ('79.119.253.220', 38972), ('38.7.250.73', 7746), ('121.98.62.85', 31264), ('45.238.115.45', 36202), ('0.0.0.0', 65535), ('95.160.156.160', 39867), ('111.0.64.42', 40048), ('104.221.97.24', 48392), ('46.6.2.112', 64856), ('91.208.206.239', 50000), ('37.187.89.189', 55013), ('31.0.121.141', 29499), ('212.239.175.11', 21552), ('79.118.13.93', 51413), ('86.10.5.251', 19098), ('42.2.47.9', 38404), ('167.40.17.252', 8000), ('187.246.171.5', 53593), ('81.182.185.18', 12627), ('31.0.33.27', 43619), ('243.35.113.201', 51413), ('88.15.7.101', 17165), ('81.33.249.181', 35308), ('41.222.248.111', 16909), ('66.115.142.186', 31698), ('49.228.105.91', 8999), ('32.1.8.248', 5677), ('106.203.254.46', 6881), ('0.0.13.221', 48392), ('188.83.68.14', 0), ('138.117.178.225', 60024), ('83.51.44.250', 9080), ('212.251.172.15', 59389), ('37.19.198.94', 62414), ('37.133.240.208', 62786), ('49.145.128.113', 20338), ('108.191.191.222', 10213), ('68.235.43.86', 39207), ('45.86.56.67', 8999), ('181.231.42.196', 51413), ('102.129.145.168', 51911), ('110.50.85.144', 21336), ('109.166.137.125', 25028), ('243.122.67.198', 48392), ('136.158.49.75', 6881), ('77.139.198.161', 47203), ('115.134.109.189', 34445), ('112.205.224.224', 49425), ('105.244.26.117', 30754), ('176.205.102.125', 8000), ('0.0.0.0', 0), ('186.96.210.98', 36048), ('31.0.0.0', 0)}
tracker.get_peer_list()
p = PeerManager(tracker)
p.connect()
print(tracker.peers)
# print(tracker.torrent_obj.total_length)
# print(len(p.piece_manager.pieces))

# f = open("ba.pdf", "wb")
# convert to while
# i = 0
# # for i, piece in enumerate(p.piece_manager.pieces):
# while i < len(p.piece_manager.pieces):
#     piece = p.piece_manager.pieces[i]
#     print("--------------------")
#     print(piece.piece_index)
#     peer = p.get_peers_having_piece(piece)
#     re = p.request_pieceByteString(piece)
#     check = 0
#     complete_piece = b''
#     j = 0
#     # for j, r in enumerate(re):
#     while j < len(re):
#         r = re[j]
#         print("-------")
#         for peer in peers:
#             if peer.sock:
#                 try:
#                     peer.sock.send(r)
#                 except:
#                     continue 
#                 data = p.read_piece_response(peer.sock, struct.unpack(">IBIII", r)[4])
#                 if data == None:
#                     continue
#                 # piece.blocks[j].data = data
#                 # check += 1
#                 print(j, len(data))
#                 complete_piece += data
#                 break
#         j += 1
#     print(piece.piece_sha1, hashlib.sha1(complete_piece).digest())
#     # if piece.piece_sha1 == hashlib.sha1(complete_piece).digest(): 
#     # f.seek(0, 2)
#     # f.write(complete_piece)         
#     # print()
#     break
#     i += 1
# # f.close()
# #write into_file
threads = []
while p.piece_manager.all_piece_complete() == False:
    for piece in p.piece_manager.pieces:
        piece_index = piece.piece_index 
        if piece.is_complete() == True:
            continue
        peer = p.get_peer_having_piece(piece)
        if peer == None:
            continue
        block_index, block_obj = piece.get_empty_block()
        request_block = p.request_blockByteString(piece, block_index, block_obj)
        try:
            peer.sock.send(request_block)
        except:
            continue        
        t = threading.Thread(target=PeerManager._read_from_socket, args = (peer.sock, piece, block_index, block_obj,))
        t.start()
        threads.append(t)
        time.sleep(5)
for process in threads:
    process.join()
                

print("Torrent Completed")
f = open(tracker.torrent_obj.name, "wb")
for piece in p.piece_manager.pieces:
    for block in piece.blocks:
        f.write(block.data)
f.close()










