import os
import socket
import threading
from queue import Queue
import signal
import sys

class Coordenador:
    def __init__(self, host='localhost', port=12345):
        self.fila = Queue()
        self.lock = threading.Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)

        signal.signal(signal.SIGINT, self.signal_handler)

        self.process_thread = threading.Thread(target=self.process_requests)
        self.process_thread.start()

        self.grants_enviados = {}

    def process_requests(self):
        while True:
            client, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                break
            if mensagem.startswith('1'):  # REQUEST
                self.request(client)
            elif mensagem.startswith('3'):  # RELEASE
                self.release()
                self.grant()
        client.close()

    def request(self, client):
        with self.lock:
            if self.fila.empty():
                client.send('GRANT'.encode('utf-8'))
            process_id = os.getpid()
            self.fila.put((client, process_id))

    def grant(self):
        with self.lock:
            if not self.fila.empty():
                next_process = self.fila.queue[0]
                next_process_socket = next_process[0]
                next_process_pid = next_process[1]
                next_process_socket.send('GRANT'.encode('utf-8'))
                self.update_grants_enviados(next_process_pid)

    def release(self):
        with self.lock:
            if not self.fila.empty():
                self.fila.get()

    def update_grants_enviados(self, pid):
        if pid in self.grants_enviados:
            self.grants_enviados[pid] += 1
        else:
            self.grants_enviados[pid] = 1

    def signal_handler(self, sig, frame):
        self.server.close()
        sys.exit(0)

if __name__ == '__main__':
    coordenador = Coordenador()
    coordenador.process_thread.join()
