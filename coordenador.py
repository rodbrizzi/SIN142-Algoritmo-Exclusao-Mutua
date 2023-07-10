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
        self.is_running = True
        self.process_thread.start()

        self.grants_enviados = {}

        self.interface_thread = threading.Thread(target=self.run_interface)
        self.interface_thread.start()

    def process_requests(self):
        while self.is_running:
            try:
                client, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(client,)).start()
            except OSError:
                break

    def handle_client(self, client):
        while True:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                break
            if mensagem.startswith('1|'):  # REQUEST
                process_id = mensagem.split('|')[1]
                self.request(client, process_id)
            elif mensagem.startswith('3'):  # RELEASE
                self.release()
                self.grant()
        client.close()

    def request(self, client, process_id):
        with self.lock:
            if self.fila.empty():
                self.update_grants_enviados(process_id)
                client.send('GRANT'.encode('utf-8'))
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
        self.is_running = False
        self.server.close()
        sys.exit(0)

    def run_interface(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Limpa o prompt de comando
            comando = input("Comandos:\n1 - Imprimir fila de pedidos atual\n2 - Imprimir quantas vezes cada processo foi atendido\n3 - Encerrar a execução\n\nDigite o número do comando: ")
            
            if comando == '1':
                self.print_current_queue()
                input("\nAperte qualquer tecla para voltar ao menu...")
            elif comando == '2':
                self.print_grants_count()
                input("\nAperte qualquer tecla para voltar ao menu...")
            elif comando == '3':
                self.shutdown()
                break
            else:
                print("Comando inválido. Tente novamente.")
                input("Aperte qualquer tecla para continuar...")

    def print_current_queue(self):
        with self.lock:
            print("Fila de Pedidos:")
            for i, item in enumerate(self.fila.queue):
                pid = item[1]
                print(f"Posição: {i}, PID: {pid}")

    def print_grants_count(self):
        with self.lock:
            print("PID    | GRANTS RECEBIDOS")
            for pid, count in self.grants_enviados.items():
                print(f"{pid} | {count}")

    def shutdown(self):
        self.is_running = False
        self.server.close()
        print("Programa finalizado.")

if __name__ == '__main__':
    coordenador = Coordenador()
    coordenador.process_thread.join()
    coordenador.interface_thread.join()
