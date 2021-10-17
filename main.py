from torrent import Torrent
from tracker import Tracker
from PeerManager import PeerManager
tracker = Tracker("torrents/torrent1.torrent")
tracker.get_peer_list()
p = PeerManager(tracker)
p.connect()