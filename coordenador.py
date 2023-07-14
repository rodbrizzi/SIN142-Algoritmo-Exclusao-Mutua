import os
import signal
import socket
import sys
import threading
from queue import Queue

# Definição do endereço IP e Porta do servidor
HOST = 'localhost'
PORT = 12345

class Coordenador:
    def __init__(self, host=HOST, port=PORT):
        """Inicia os atributos do objeto."""
        # Gerencia as threads
        self.is_running = True
        self.lock = threading.Lock()

        # Configura o servidor
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Gerencia a fila
        self.fila = Queue()
        self.grants_enviados = {}

        # Inicia as threads de processamento e interface
        self.process_thread = threading.Thread(target=self.process_requests)
        self.process_thread.start()
        self.interface_thread = threading.Thread(target=self.run_interface)
        self.interface_thread.start()

    def process_requests(self):
        # Processa as requisições enquanto a aplicação estiver rodando
        while self.is_running:
            try:
                client, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(client,)).start()
            except OSError:
                break

    def handle_client(self, client):
        # Manipula a conexão com o cliente
        while True:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                break
            if mensagem.startswith('1|'):  # RECEBE REQUEST
                process_id = mensagem.split('|')[1]
                self.request(client, process_id)
            elif mensagem.startswith('3'):  # RECEBE RELEASE
                self.release()
                self.grant()
        client.close()

    def request(self, client, process_id):
        # Processa uma requisição de um cliente
        with self.lock:
            if self.fila.empty():
                self.update_grants_enviados(process_id)
                client.send(self._criar_mensagem('2', process_id).encode('utf-8')) #ENVIA GRANT
            self.fila.put((client, process_id))

    def grant(self):
        # Concede permissão para um cliente
        with self.lock:
            if not self.fila.empty():
                next_process = self.fila.queue[0]
                next_process_socket = next_process[0]
                next_process_pid = next_process[1]
                next_process_socket.send(self._criar_mensagem('2', next_process_pid).encode('utf-8')) #ENVIA GRANT
                self.update_grants_enviados(next_process_pid)

    def release(self):
        # Libera um recurso
        with self.lock:
            if not self.fila.empty():
                self.fila.get()

    def update_grants_enviados(self, pid):
        # Atualiza a contagem de GRANTs enviados
        if pid in self.grants_enviados:
            self.grants_enviados[pid] += 1
        else:
            self.grants_enviados[pid] = 1

    def _criar_mensagem(self, codigo, pid):
        # Cria uma mensagem para o cliente
        return f'{codigo}|{pid}|' + ''.join(['0' for _ in range(10 - len(codigo) - len(str(pid)) - 2)])

    def signal_handler(self, sig, frame):
        # Encerra a aplicação quando o sinal SIGINT é recebido
        self.is_running = False
        self.server.close()
        sys.exit(0)

    def run_interface(self):
        # Roda a interface do usuário
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
        # Imprime a fila atual
        with self.lock:
            print("\nFila de Pedidos:\n")
            print("PID    | POSIÇÃO")
            for i, item in enumerate(self.fila.queue):
                pid = item[1]
                print(f"{pid} | {i+1}º")

    def print_grants_count(self):
        # Imprime a quantidade de GRANTs por PID
        with self.lock:
            print("\nPID    | QUANTIDADE DE GRANTS")
            for pid, count in self.grants_enviados.items():
                print(f"{pid} | {count}")

    def shutdown(self):
        # Encerra a execução do coordenador
        self.is_running = False
        self.server.close()
        print("Programa finalizado.")

def main():
    """Função principal que inicia o coordenador e aguarda as threads terminarem."""
    coordenador = Coordenador()
    coordenador.process_thread.join()
    coordenador.interface_thread.join()

if __name__ == '__main__':
    main()
