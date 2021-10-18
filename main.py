from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
tracker = Tracker("torrents/torrent6.torrent")
tracker.peers = [('32.1.8.248', 5677), ('105.244.128.183', 45021), ('234.113.210.189', 8000)]
p = PeerManager(tracker)
p.connect()