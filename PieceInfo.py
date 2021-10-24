from torrent import Torrent
from math import ceil
from BlockandPiece import Piece
class PieceInfo:
    def __init__(self, torrent):
        self.torrent = torrent
        self.number_of_pieces = ceil(torrent.total_length / torrent.piece_length)
        self.pieces = []
        self.pieces_SHA1 = []
        self.getSHA1()
        self.generate_piece()

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

          