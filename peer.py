import socket
from ipaddress import ip_address, IPv4Address
def validIPAddress(IP: str) -> str:
    try:
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"
class peer:
    def __init__(self, ip_port):
        self.sock = None
        self.ip_port = ip_port
    def connect_to_peer(self):
        if validIPAddress(self.ip_port[0]) == "IPv6":
            self.ip_port = (self.ip_port[0], self.ip_port[1], 0, 0)
        print("Attempting connection to ", self.ip_port)
        try:
            self.sock = socket.create_connection(self.ip_port, timeout=20)
            print("Success")
        except Exception as e:
            print(e)
    



            