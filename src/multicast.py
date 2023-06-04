import socket
import threading
import time
import multiprocessing

MULTICAST_GROUP = '224.0.0.1'
MULTICAST_PORT = 5000

class HeartbeatProcess:
    def __init__(self, process_name, send_interval, receive_interval):
        self.process_name = process_name
        self.send_interval = send_interval
        self.receive_interval = receive_interval
        self.sock = None
        self.suspected = []
        self.last_heartbeat_times = {}

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MULTICAST_PORT))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0'))

        send_thread = threading.Thread(target=self.send_heartbeat)
        receive_thread = threading.Thread(target=self.receive_heartbeat)
        check_suspected_thread = threading.Thread(target=self.check_suspected)

        send_thread.start()
        receive_thread.start()
        check_suspected_thread.start()

    def send_heartbeat(self):
        while True:
            message = f"Heartbeat from {self.process_name}".encode()
            self.sock.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))
            self.last_heartbeat_times[self.process_name] = time.time()
            # print(f"Enviado heartbeat de {self.process_name}")
            time.sleep(self.send_interval)

    def receive_heartbeat(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            if data:
                sender_process = data.decode().split(" ")[2]
                # print(f"Recebido heartbeat de {sender_process}")
                self.last_heartbeat_times[sender_process] = time.time()
                if sender_process in self.suspected:
                    self.suspected.remove(sender_process)
                    print(f"Removido {sender_process} da lista de suspeitos")
            time.sleep(self.receive_interval)

    def check_suspected(self):
        while True: 
            current_time = time.time()
            for process, last_heartbeat_time in self.last_heartbeat_times.items():
                if current_time - last_heartbeat_time > 3 and process != self.process_name:
                    if process not in self.suspected:
                        self.suspected.append(process)
                        print(f"Adicionado {process} à lista de suspeitos")
            print(f"Lista de suspeitos de {self.process_name} = {self.suspected}")

# Função para iniciar o HeartbeatProcess
def start_heartbeat_process(process_name, send_interval, receive_interval):
    heartbeat_process = HeartbeatProcess(process_name, send_interval, receive_interval)
    heartbeat_process.start()

if __name__ == '__main__':
    # Criação dos processos
    process1 = multiprocessing.Process(target=start_heartbeat_process, args=("Process1", 3, 1))
    process2 = multiprocessing.Process(target=start_heartbeat_process, args=("Process2", 3, 1))
    process3 = multiprocessing.Process(target=start_heartbeat_process, args=("Process3", 3, 1))

    # Inicialização dos processos
    process1.start()
    process2.start()
    process3.start()

    try:
        # Mantém a função principal em execução
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Interrompe a execução dos processos ao pressionar Ctrl+C
        process1.terminate()
        process2.terminate()
        process3.terminate()

        process1.join()
        process2.join()
        process3.join()
