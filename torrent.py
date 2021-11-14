from bcoding import bencode, bdecode
import sys
import os
import hashlib
import time

class Torrent:
    def __init__(self,torrent_path, file_path):
        self.torrent_path = torrent_path
        self.file_path = file_path
        self.decode_bencoded_file()
        self.initialize_files()
        self.request_peers_parameters()
    def decode_bencoded_file(self):
        with open(self.torrent_path, 'rb') as file:
            contents = bdecode(file)
        with open('torrent.txt', 'w') as file:
            for key, value in contents.items():
                file.write(f"{str(key)} : {str(value)}")
                file.write("\n\n")
        self.contents = contents
        self.announce_list = []
        if "announce-list" in self.contents:
            self.announce_list = [x[0] for x in self.contents["announce-list"]]
        else:
            self.announce_list = [self.contents["announce"]]
        # self.comment = self.contents["comment"]
        # self.creation_date = self.contents["created by"]
        #self.encoding = self.contents["encoding"]
        self.multipleFiles = False
        if "files" in self.contents["info"]:
            self.multipleFiles = True
            self.files = self.contents["info"]["files"]
        else:
            file_dictionary = {"length" : self.contents["info"]["length"], "path" : ""}
            self.files = [file_dictionary]
        self.name = self.contents["info"]["name"]
        self.piece_length = self.contents["info"]["piece length"]
        self.pieces = self.contents["info"]["pieces"]

    #init files
    def initialize_files(self):
        total_length = 0
        self.total_path = self.file_path
        if self.multipleFiles == True:
            root_folder_name = self.name
            self.total_path = os.path.join(self.file_path, root_folder_name)
            print(self.total_path)
            if not os.path.exists(self.total_path):
                os.mkdir(self.total_path, 0o777)
            for file in self.files:
                path_file = os.path.join(self.total_path, *file["path"])

                if not os.path.exists(os.path.dirname(path_file)):
                    os.makedirs(os.path.dirname(path_file))

                total_length += file["length"]
        else:
            total_length = int(self.files[0]["length"])
        self.total_length = total_length
        
    def request_peers_parameters(self):
        bencoded_info = bencode(self.contents["info"])
        self.info_hash = hashlib.sha1(bencoded_info).digest()
        self.peer_id = self.generate_peer_id()
        self.left = self.total_length
        self.port = 6889

    def generate_peer_id(self):
        seed = str(time.time())
        return hashlib.sha1(seed.encode('utf-8')).digest()

