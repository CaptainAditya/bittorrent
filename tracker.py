from torrent import Torrent
from bcoding import bencode, bdecode
from udp import udpTracker
import requests
import struct
import random
import socket
import time
from urllib.parse import urlparse

class Tracker:
    def __init__(self, torrent_path):
        self.torrent_obj = Torrent(torrent_path)
    def get_peer_list(self):
        params = {
            'info_hash': self.torrent_obj.info_hash,
            'peer_id': self.torrent_obj.peer_id,
            'uploaded': 0,
            'downloaded': 0,
            'port': 6881,
            'left': self.torrent_obj.left,
            'event' : 'started'
        }
        for url in self.torrent_obj.announce_list:
            if "udp" in url:
                self.udp_request(url)

    
    def http_request(self, tracker_url):
        params = {
            'info_hash': self.torrent_obj.info_hash,
            'peer_id': self.torrent_obj.peer_id,
            'uploaded': 0,
            'downloaded': 0,
            'port': self.torrent_obj.port,
            'left': self.torrent_obj.left,
            'event' : 'started'
        }            
        try:
            answer_tracker = requests.get(tracker_url, params=params, timeout=5)
            list_peers = bdecode(answer_tracker.content)
            print(list_peers)
        except Exception as e:
            print("HTTP scraping failed: %s" % e.__str__())

    def udp_request(self, tracker_url):
        url_parse = urlparse(tracker_url)
        host = ".".join(url_parse.hostname.split(".")[1:])
        try:
            ip, port = socket.gethostbyname(url_parse.hostname), url_parse.port
        except Exception as e:
            print(e.__str__())
        return


t = Tracker("torrent2.torrent")  
t.get_peer_list()