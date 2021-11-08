from torrent import Torrent
import ipaddress
from bcoding import bencode, bdecode
from udp import udpTrackerAnnouncing, udpTrackerConnecting
import requests
import struct
import random
import socket
import time
import errno

from urllib.parse import urlparse
import threading
class Tracker:
    def __init__(self, torrent_path):
        self.torrent_obj = Torrent(torrent_path) 
        self.peers = set()
        self.tracker_threads = []
    def get_peer_list(self):
        for url in self.torrent_obj.announce_list:
            t = None
            if "http" in url:
                t = threading.Thread(target=self.http_request, args = (url,))
                # self.http_request(url)
            if "udp" in url:
                t = threading.Thread(target=self.udp_request, args = (url,))
            t.start()
            self.tracker_threads.append(t)
                # self.udp_request(url)
    def exitAllThreads(self):
        for thread in self.tracker_threads:
            thread.join()
    def http_request(self, tracker_url):
        url_parse = urlparse(tracker_url)
        payload = {'info_hash': self.torrent_obj.info_hash, 
                    'peer_id': self.torrent_obj.peer_id, 
                    'uploaded': 0, 
                    'downloaded': 0, 
                    'port': 6881, 
                    'left': self.torrent_obj.total_length, 
                    'event': 'started'}
        try:
            answer_tracker = requests.get(tracker_url, params=payload, timeout=5)
            response = bdecode(answer_tracker.content)
            print(response)
            self.peers[tracker_url] = []
            offset=0
            if type(response['peers']) != dict:
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
                    # self.peers[tracker_url].append(ip_port)
                    self.peers.add(ip_port)
            else:
                for p in response['peers']:
                    # self.peers[tracker_url].append((p['ip'], p['port']))
                    ip_port = (p['ip'], p['port'])
                    self.peers.add(ip_port)
        except Exception as e:
            return
    def udp_request(self, tracker_url):
        print(tracker_url)
        url_parse = urlparse(tracker_url)
        ipv6 = False
        tracker_connection = udpTrackerConnecting()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)          
        try:
            sock.sendto(tracker_connection.bytestringForConnecting(), (url_parse.hostname, url_parse.port))
        except socket.gaierror:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            try:   
                sock.sendto(tracker_connection.bytestringForConnecting(), (url_parse.hostname, url_parse.port, 0 , 0))
            except:
                return
        sock.settimeout(10) 
        try:
            data, addr = sock.recvfrom(131072)
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
        sock.settimeout(10) 
        completeMessage = b'' 

        while True:
            try:
                data,addr = sock.recvfrom(4096)
                if len(data) <= 0:
                    break
                completeMessage += data
            except socket.error as e:
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    pass
                break
            except Exception:
                break
        if len(completeMessage) <= 0:
            return
        ip_ports = tracker_announce.parse_response(completeMessage)
        # self.peers[tracker_url] = ip_ports
        for x in ip_ports:
            self.peers.add(x)
        print(ip_ports)