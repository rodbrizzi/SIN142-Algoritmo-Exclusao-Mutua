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
        #print('Coordenador ouvindo em', host, port)

        # Define um tratador para o sinal SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.process_thread = threading.Thread(target=self.process_requests)
        self.process_thread.start()

    def process_requests(self):
        while True:
            client, addr = self.server.accept()
            #print('Conexão de', addr)
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                break
            #print('Mensagem recebida:', mensagem)
            if mensagem.startswith('1'):  # REQUEST
                self.request(client)
            elif mensagem.startswith('3'):  # RELEASE
                self.release()
                self.grant()
        client.close()

    def request(self, client):
        with self.lock:
            if self.fila.empty():
                #print('GRANT enviado')
                client.send('GRANT'.encode('utf-8'))
            self.fila.put(client)

    def grant(self):
        with self.lock:
            if not self.fila.empty():
                next_process = self.fila.queue[0]
                #print('GRANT enviado')
                next_process.send('GRANT'.encode('utf-8'))

    def release(self):
        with self.lock:
            if not self.fila.empty():
                self.fila.get()
                #print('RELEASE recebido')

    def signal_handler(self, sig, frame):
        #print('Programa finalizado. Fechando o servidor...')
        self.server.close()
        sys.exit(0)

if __name__ == '__main__':
    coordenador = Coordenador()
    coordenador.process_thread.join()
