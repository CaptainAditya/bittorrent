
import struct
from bitstring import *
from BlockandPiece import Piece
class keep_alive:
    # keep-alive: <len=0000>
    length = 0
    def __init__(self):
        return
    def byteStringForKeepAlive(self):
        return struct.pack('>I', self.length)
    
class chock:
    # choke: <len=0001><id=0>
    length = 1
    message_ID = 0

    def __init__(self) -> None:
        pass
    @classmethod
    def parse_response(self, response):
        length, message_ID = struct.unpack(">IB", response[:5])
        if length == self.length and message_ID == self.message_ID:
            return 1
        else: return -1

class unchoke:
    # unchoke: <len=0001><id=1>
    length = 1
    message_ID = 1

    def __init__(self):
        return
    @classmethod
    def parse_response(self, response):
        length, message_id = struct.unpack('>IB', response[:5])
        if length == self.length and message_id == self.message_ID:
            return 1
        else:
            return -1

class interested:
    # interested: <len=0001><id=2>
    length = 1
    message_ID = 2
    def __init__(self):
        return
    def byteStringForInterested(self):
        return struct.pack('>IB', self.length, self.message_ID)

class not_interested:
    # not interested: <len=0001><id=3>
    length = 1
    message_ID = 3
    def __init__(self) -> None:
        pass
    def byteStringForNotInterested(self):
        return struct.pack(">IB", self.length, self.message_ID)
    
class have:
    # have: <len=0005><id=4><piece index>
    length = 5
    message_ID = 4
    def __init__(self, piece_index) -> None:
        self.piece_index = piece_index
    @classmethod
    def parse_response(self, response):
        length, message_ID, piece_index = struct.unpack(">IBI", response[:9])
        if length == self.length and message_ID == self.message_ID:
            return have(piece_index)
        return -1

class Bitfield:
    # bitfield: <len=0001+X><id=5><bitfield>
    length = None
    message_ID = 5

    def __init__(self, bitfield):
        self.bitfield = bitfield
        self.bitfield_as_bytes = bitfield.tobytes()
        self.bitfield_length = len(self.bitfield_as_bytes)
        self.length = 1 + self.bitfield_length
    @classmethod
    def parse_response(cls, response):
        length, message_ID = struct.unpack(">IB", response[:5])
        bitfield_length = length - 1
        if message_ID == cls.message_ID:
            raw_bytes, = struct.unpack(f">{bitfield_length}s", response[5 : 5 + bitfield_length])
            bitfield = BitArray(bytes = bytes(raw_bytes))
            print("Bitfield")
            return Bitfield(bitfield)
        else:
            return -1

class request:
    # request: <len=0013><id=6><index><begin><length>
    length = 13
    message_ID = 6
    def __init__(self, piece_index, piece_offset, block_length):
        self.piece_index = piece_index
        self.piece_offset = piece_offset
        self.block_length = block_length
    def byteStringForRequest(self):
        return struct.pack(">IBIII", self.length, self.message_ID, self.piece_index, self.piece_offset, self.block_length)

class pieceMessage:
    # piece: <len=0009+X><id=7><index><begin><block>
    length = None
    message_ID = 7
    def __init__(self):
        return
    @classmethod
    def parse_response(cls, response):
        block_length = len(response) - 13
        length, message_ID, piece_index, block_offset , block= struct.unpack(f"IBII{block_length}s", response[:13 + block_length])
        if cls.message_ID == message_ID:
            return (piece_index, block_length, block_offset, block)      
        else:
            return -1

class ParseMessageFromPeer:
    id = {
        0 : chock,
        1 : unchoke,
        2 : interested,
        3 : not_interested,
        4 : have,
        5 : Bitfield,
        6 : request,
        7 : pieceMessage
    }
    def __init__(self):
        return
    @classmethod
    def parse_response(cls, response):
        length, message_ID = struct.unpack(">IB", response[:5])


