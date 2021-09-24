from bcoding import bencode, bdecode
import sys
import os
import hashlib
import time
class Torrent:
    def __init__(self,torrent_path):
        self.torrent_path = torrent_path

    def decode_bencoded_file(self):
        with open(self.torrent_path, 'rb') as file:
            contents = bdecode(file)
        self.contents = contents
        self.announce_list = []
        if "announce-list" in self.contents:
            self.announce_list = self.contents["announce-list"]
        else:
            self.announce_list = [self.contents["announce"]]
        self.comment = self.contents["comment"]
        self.creation_date = self.contents["created by"]
        #self.encoding = self.contents["encoding"]
        self.multipleFiles = False
        if "files" in self.contents["info"]:
            self.multipleFiles = True
            self.files = self.contents["info"]["files"]
        else:
            file_dictionary = {"length" : self.contents["info"]["length"]}
            self.files = [file_dictionary]
        self.name = self.contents["info"]["name"]
        self.piece_length = self.contents["info"]["piece length"]
        self.pieces = self.contents["info"]["pieces"]

    #init files
    def initialize_files(self):
        total_length = 0
        if self.multipleFiles == True:
            root_folder_name = self.name
            if not os.path.exists(root_folder_name):
                os.mkdir(root_folder_name, 0o777)
            
            for sub_folder in self.files:
                path_file = os.path.join(root_folder_name, *sub_folder["path"])
                if not os.path.exists(os.path.dirname(path_file)):
                    os.make_(os.path.dirname(path_file))
                total_length += int(sub_folder["length"])
        else:
            total_length = int(self.files[0]["length"])
        self.total_length = total_length
        
    def request_peers_parameters(self):
        bencoded_info = bencode(self.contents["info"])
        self.info_hash = hashlib.sha1(bencoded_info).digest()
        self.peer_id = hashlib.sha1('-AZ2200-6wfG2wk6wWLc'.encode('utf-8')).digest()
        self.left = self.total_length
    

    

path = sys.argv[1]
torrent = Torrent(path)
torrent.decode_bencoded_file()
torrent.initialize_files()
print(torrent.announce_list)