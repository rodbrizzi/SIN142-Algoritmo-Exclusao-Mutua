import socket
import threading
from collections import deque
import time

COORDINATOR_HOST = 'localhost'
COORDINATOR_PORT = 12345
SEPARATOR = '|'
MESSAGE_SIZE = 10

message_queue = deque()  # Fila FIFO para armazenar as mensagens

def handle_connection(client_socket, client_address):
    try:
        print(f"Conexão estabelecida com {client_address}")

        # Recebe a mensagem do processo
        message = client_socket.recv(MESSAGE_SIZE).decode()

        # Enfileira a mensagem
        message_queue.append(message)

    finally:
        # Fecha o socket do cliente
        client_socket.close()

def process_message_queue():
    while True:
        if message_queue:
            # Processa a mensagem mais antiga da fila
            message = message_queue.popleft()

            # Imprime a mensagem
            print("Mensagem recebida:", message)
        else:
            # Aguarda um curto período de tempo se a fila estiver vazia
            time.sleep(0.1)

def start_coordinator():
    # Cria um socket TCP/IP
    coordinator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Vincula o socket à porta e endereço do coordenador
    coordinator_socket.bind((COORDINATOR_HOST, COORDINATOR_PORT))

    # Coloca o socket em modo de escuta
    coordinator_socket.listen(1)

    print("Coordenador iniciado. Aguardando conexões...")

    # Inicia a thread para processar a fila de mensagens
    processing_thread = threading.Thread(target=process_message_queue)
    processing_thread.start()

    while True:
        # Aguarda uma conexão
        client_socket, client_address = coordinator_socket.accept()

        # Cria uma nova thread para tratar a conexão
        connection_thread = threading.Thread(target=handle_connection, args=(client_socket, client_address))
        connection_thread.start()

# Inicia o processo coordenador
start_coordinator()
