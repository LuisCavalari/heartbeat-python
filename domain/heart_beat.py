import socket
import threading
import time
from infraestructure.multicast_socket import MultiCastSocketFactory
class HeartbeatProcess:
    def __init__(self, process_name, send_interval, receive_interval):
        self.process_name = process_name
        self.send_interval = send_interval
        self.receive_interval = receive_interval
        self.sock = None
        self.suspected = []
        self.last_heartbeat_times = {}

    def start(self):
        self.sock = MultiCastSocketFactory().create_multicast_socket()
        send_thread = threading.Thread(target=self.send_heartbeat)
        receive_thread = threading.Thread(target=self.receive_heartbeat)
        check_suspected_thread = threading.Thread(target=self.check_suspected)

        send_thread.start()
        receive_thread.start()
        check_suspected_thread.start()

    def send_heartbeat(self):
        while True:
            message = f"Heartbeat de {self.process_name}".encode()
            self.sock.send_to_all_members(message)
            self.last_heartbeat_times[self.process_name] = time.time()
            time.sleep(self.send_interval)

    def receive_heartbeat(self):
        while True:
            data, _ = self.sock.receive_from_buffer()
            if data:
                sender_process = data.decode().split(" ")[2]
                self.last_heartbeat_times[sender_process] = time.time() 
                if sender_process in self.suspected:
                    self.suspected.remove(sender_process)
                    print(f"Removido {sender_process} da lista de suspeitos do {self.process_name}")
            time.sleep(self.receive_interval)

    def check_suspected(self):
        while True: 
            current_time = time.time()
            for process, last_heartbeat_time in self.last_heartbeat_times.items():
                if current_time - last_heartbeat_time > (self.send_interval*2.5) and process != self.process_name:
                    if process not in self.suspected:
                        self.suspected.append(process)
                        print(f"Adicionado {process} à lista de suspeitos")
            if self.suspected:
                    print(f"Lista de suspeitos de {self.process_name} = {self.suspected}")
            time.sleep(self.receive_interval/2)