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

tracker = Tracker("torrents/singleFile.torrent")
# tracker.peers = {('31.217.15.226', 62734), ('64.188.185.126', 8999), ('41.212.58.184', 35368), ('0.0.0.0', 0), ('199.88.191.59', 40810), ('199.187.210.214', 44278), ('0.0.0.0', 65535), ('134.2.214.194', 8000), ('87.5.69.217', 53650), ('105.244.106.4', 11691), ('222.173.52.178', 51413), ('176.205.102.125', 8000), ('32.1.8.248', 5677), ('64.188.185.126', 0), ('105.163.210.73', 19794), ('162.216.47.200', 40810), ('41.204.60.46', 57235), ('196.64.134.88', 14781), ('185.192.70.17', 46774), ('94.140.9.181', 18194), ('135.148.100.25', 52963)}
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
# threads = []
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
        # t = threading.Thread(target=PeerManager._read_from_socket, args = (peer.sock, piece, block_index, block_obj,))
        # t.start()
        # threads.append(t)
        # def _read_from_socket(sock:socket.socket, piece:Piece, block_index, block_obj : Block):
        data = b''
        peer.sock.settimeout(10)
        while True:
            try:
                buff = peer.sock.recv(4096)
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
            continue
        
        piece.blocks[block_index].status = 1
        piece.blocks[block_index].data = data
        print(piece.piece_index, block_index, len(data))
# for process in threads:
#     process.join()
                

print("Torrent Completed")
f = open(tracker.torrent_obj.name, "wb")
for piece in p.piece_manager.pieces:
    for block in piece.blocks:
        f.write(block.data)
f.close()










