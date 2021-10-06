from torrent import Torrent
from bcoding import bencode, bdecode
from udp import udpTrackerAnnouncing, udpTrackerConnecting
import requests
import struct
import random
import socket
import time
from urllib.parse import urlparse

class Tracker:
    def __init__(self, torrent_path):
        self.torrent_obj = Torrent(torrent_path)
        self.peers = []
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
            if "http" in url:
                # self.http_request(url)
                pass
            elif "udp" in url:
                self.udp_request(url)
            else:
                print("Unknown URL format")
        print(self.peers)

    
    def http_request(self, tracker_url):
        params = {
            'info_hash': self.torrent_obj.info_hash,
            'peer_id': self.torrent_obj.peer_id,
            'left': self.torrent_obj.left,            
        }            
        try:
            answer_tracker = requests.get(tracker_url, params=params, timeout=5)
            print(answer_tracker.status_code)
            
        except Exception as e:
            print("HTTP scraping failed: %s" % e.__str__())

    def udp_request(self, tracker_url):
        url_parse = urlparse(tracker_url)
        def resolveHost(parse):
            try:
                ip, port = socket.gethostbyname(parse.hostname), parse.port
            except:
                return "", 0
            return ip, port
        ip, port = resolveHost(url_parse)
        if (ip, port) == ("", 0) or ip == "127.0.0.1":
            return "DNS"
        print(ip, port)
        
        tracker_connection = udpTrackerConnecting()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)       
        sock.settimeout(7) 
        sock.sendto(tracker_connection.bytestringForConnecting(), (ip, port))
        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout:
            return
        tracker_connection.parse_response(data)
        sender_port = sock.getsockname()[1]

        tracker_announce = udpTrackerAnnouncing(tracker_connection.server_connection_id, self.torrent_obj.info_hash, 
                                                self.torrent_obj.peer_id, self.torrent_obj.left, sender_port)
        sock.sendto(tracker_announce.byteStringAnnounce(), (ip, port))
        try:
            data,addr = sock.recvfrom(4096)
        except:
            return

        ip_ports = tracker_announce.parse_response(data)
        
        for x in ip_ports:
            self.peers.append(x)



    
t = Tracker("torrent1.torrent")  
t.get_peer_list()