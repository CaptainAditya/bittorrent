BLOCK_SIZE = 16384
from math import ceil
class Block:
    def __init__(self, block_size = BLOCK_SIZE, raw_bytes = b""):
        self.block_size = block_size
        self.data = raw_bytes

class Piece:
    def __init__(self, piece_index, piece_size, piece_sha1):
        self.piece_index = piece_index
        self.piece_size = piece_size
        self.piece_sha1 = piece_sha1
        self.number_of_blocks = ceil(self.piece_size // BLOCK_SIZE)
        self.blocks: list[Block] = []
    def init_blocks(self):
        if self.number_of_blocks > 1:
            for i in range(self.number_of_blocks):
                self.blocks.append(Block())
            if self.piece_size % BLOCK_SIZE > 0:
                self.blocks[self.number_of_blocks - 1].block_size = self.piece_size % BLOCK_SIZE
        else:
            self.blocks.append(Block(self.piece_size))
    
                

        
