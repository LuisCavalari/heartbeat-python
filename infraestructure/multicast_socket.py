import socket

MULTICAST_GROUP = '224.0.0.1'
MULTICAST_PORT= 5000

class MultiCastSocketFactory:
    def create_multicast_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MULTICAST_PORT))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0'))
        return self
        
    def send_to_all_members(self, message):
        self.sock.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))

    def receive_from_buffer(self, size = 1024):
        return self.sock.recvfrom(size)

