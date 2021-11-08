from torrent import Torrent
from math import ceil
from BlockandPiece import Piece
import random
import colorama
from colorama import Fore, Back, Style
import heapq as hq
colorama.init(autoreset=True)#auto resets your settings after every output

class PieceInfo:
    def __init__(self, torrent):
        self.torrent:Torrent = torrent
        self.number_of_pieces = ceil(torrent.total_length / torrent.piece_length)
        self.pieces = []
        self.pieces_SHA1 = []
        self.getSHA1()
        self.generate_piece()
        self.totalBlocks = self.getTotalBlocks()
        self.files = self._load_files()
    def generate_piece(self):
        last_piece = self.number_of_pieces - 1
        for i in range(self.number_of_pieces):
            if i == last_piece:
                piece_length = self.torrent.total_length - (self.number_of_pieces - 1) * self.torrent.piece_length
                self.pieces.append(Piece(i, piece_length, self.pieces_SHA1[i]))
            else:
                self.pieces.append(Piece(i, self.torrent.piece_length, self.pieces_SHA1[i]))
    
    def getSHA1(self):
        for i in range(self.number_of_pieces):
            start = i * 20
            end = start + 20
            self.pieces_SHA1.append(self.torrent.pieces[start : end])

    def merge_blocks(self, index):
        res = b""
        for block in self.pieces[index].blocks:
            res += block.data
        return res

    def all_piece_complete(self):
        for piece in self.pieces:
            if piece.is_complete() == False:
                return False
        return True
    
    def getRandomPiece(self):
        piece = None
        while True:
            piece : Piece = random.choice(self.pieces)
            if piece.is_complete() == False:
                return piece
    def _load_files(self):
        files = []
        piece_offset = 0
        piece_size_used = 0

        for f in self.torrent.files:
            current_size_file = f["length"]
            file_offset = 0

            while current_size_file > 0:
                id_piece = int(piece_offset / self.torrent.piece_length)
                piece_size = self.pieces[id_piece].piece_size - piece_size_used

                if current_size_file - piece_size < 0:
                    file = {"length": current_size_file,
                            "idPiece": id_piece,
                            "fileOffset": file_offset,
                            "pieceOffset": piece_size_used,
                            "path": f["path"]
                            }
                    piece_offset += current_size_file
                    file_offset += current_size_file
                    piece_size_used += current_size_file
                    current_size_file = 0

                else:
                    current_size_file -= piece_size
                    file = {"length": piece_size,
                            "idPiece": id_piece,
                            "fileOffset": file_offset,
                            "pieceOffset": piece_size_used,
                            "path": f["path"]
                            }
                    piece_offset += piece_size
                    file_offset += piece_size
                    piece_size_used = 0

                files.append(file)
        return files
    def write_into_file(self):
        master_i = 0
        n = len(self.files)
        if self.torrent.multipleFiles:
            while master_i < n:
                piece_index = self.files[master_i]['idPiece']
                length = self.files[master_i]['length']
                file_offset = self.files[master_i]['fileOffset']
                piece_offset = self.files[master_i]['pieceOffset']
                path = self.files[master_i]['path']

                if self.pieces[piece_index].is_complete == False:
                    continue
                path_to_file = "//".join(path)
                path_to_file = self.torrent.name + "//" + path_to_file
                try:
                    f = open(path_to_file, 'r+b')  # Already existing file
                except IOError:
                    f = open(path_to_file, 'wb')  # New file
                data_to_be_written = self.merge_blocks(piece_index)[piece_offset : piece_offset + length]
                f.seek(file_offset)
                f.write(data_to_be_written)
                master_i += 1
        else:
            n = self.number_of_pieces
            f = open(self.torrent.name, 'wb')  # New file
            while master_i < n:
                if self.pieces[master_i].is_complete == False:
                    continue
                data_to_be_written = self.merge_blocks(master_i)
                f.write(data_to_be_written)
                master_i += 1

    def getTotalBlocks(self):
        total = 0
        for piece in self.pieces:
            total += len(piece.blocks)
        return total
    def percentage(self):
        blocksDone = 0
        for piece in self.pieces:
            for block in piece.blocks:
                if block.status == 1 : blocksDone += 1
        percentage = (blocksDone/self.totalBlocks) * 100
        inString = "PROGRESS REPORT : " + str(percentage) + "% Downloaded"
        print (Back.GREEN + inString)

    def getRarestPieceMinHeap(self, connectedPeers):
        
        piece_numberOfpeers = {}
        for i in range(self.number_of_pieces):
            piece_numberOfpeers[i] = 0
        for peer in connectedPeers:
            if peer.bit_field:
                for index, piece in enumerate(peer.bit_field):
                    if peer.bit_field[index]:
                        piece_numberOfpeers[index] += 1
        piece_numberOfpeers = (sorted(piece_numberOfpeers.items(), key =
             lambda kv:(kv[1], kv[0])))  
        return piece_numberOfpeers
        
