from torrent import Torrent
import ipaddress
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
        self.peers = {}
    def get_peer_list(self):
        for url in self.torrent_obj.announce_list:
            if "http://p4p.arenabg.com:1337/announce" in url:
                self.http_request(url)
            # if "udp://tracker.cyberia.is:6969/announce" in url:
            #     self.udp_request(url)
        print(self.peers)  

    def http_request(self, tracker_url):
        url_parse = urlparse(tracker_url)
        payload = {'info_hash': self.torrent_obj.info_hash, 
                    'peer_id': self.torrent_obj.peer_id, 
                    'port': 6881, 
                    'uploaded': 0, 
                    'downloaded': 0, 
                    'left': self.torrent_obj.total_length, 
                    'event': 'started'}
        try:
            answer_tracker = requests.get(tracker_url, params=payload, timeout=10)
            response = bdecode(answer_tracker.content)
            print(response)
            self.peers[tracker_url] = []
            offset=0
            if not type(response['peers']) == dict:
                '''
                    - Handles bytes form of list of peers
                    - IP address in bytes form:
                        - Size of each IP: 6 bytes
                        - The first 4 bytes are for IP address
                        - Next 2 bytes are for port number
                    - To unpack initial 4 bytes !i (big-endian, 4 bytes) is used.
                    - To unpack next 2 byets !H(big-endian, 2 bytes) is used.
                '''
                for _ in range(len(response['peers'])//6):
                    ip = struct.unpack_from("!i", response['peers'], offset)[0]
                    ip = socket.inet_ntoa(struct.pack("!i", ip))
                    offset += 4
                    port = struct.unpack_from("!H",response['peers'], offset)[0]
                    offset += 2
                    ip_port = (ip,port)
                    self.peers[tracker_url].append(ip_port)
            else:
                for p in response['peers']:
                    self.peers[tracker_url].append((p['ip'], p['port']))
        except Exception as e:
            return
    def udp_request(self, tracker_url):
        print(tracker_url)
        url_parse = urlparse(tracker_url)
        ipv6 = False
        tracker_connection = udpTrackerConnecting()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
        sock.settimeout(7) 
        try:
            sock.sendto(tracker_connection.bytestringForConnecting(), (url_parse.hostname, url_parse.port))
        except socket.gaierror:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            try:   
                sock.sendto(tracker_connection.bytestringForConnecting(), (url_parse.hostname, url_parse.port, 0 , 0))
            except:
                return

        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout:
            return
        tracker_connection.parse_response(data)
        sender_port = sock.getsockname()[1]

        tracker_announce = udpTrackerAnnouncing(tracker_connection.server_connection_id, self.torrent_obj.info_hash, 
                                                self.torrent_obj.peer_id, self.torrent_obj.left, sender_port)

        try:
            sock.sendto(tracker_announce.byteStringAnnounce(), (url_parse.hostname, url_parse.port))
        except socket.gaierror:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            try:    
                sock.sendto(tracker_announce.byteStringAnnounce(), (url_parse.hostname, url_parse.port, 0, 0))
            except:
                return
            
        try:
            data,addr = sock.recvfrom(4096)
        except socket.timeout:
            return
        ip_ports = tracker_announce.parse_response(data)
        self.peers[tracker_url] = ip_ports
        

