import socket
import time

COORDINATOR_HOST = 'localhost'
COORDINATOR_PORT = 12345
SEPARATOR = '|'
MESSAGE_SIZE = 10

def send_message_to_coordinator(message):
    # Cria um socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta ao endereço e porta do coordenador
    client_socket.connect((COORDINATOR_HOST, COORDINATOR_PORT))

    try:
        # Envia a mensagem para o coordenador
        client_socket.sendall(message.encode())

    finally:
        # Fecha o socket do cliente
        client_socket.close()

def pad_message(message):
    # Preenche a mensagem com zeros para garantir o tamanho fixo
    return message.ljust(MESSAGE_SIZE, '0')

def create_request_message(process_id):
    # Cria uma mensagem de REQUEST com o código 1 e o identificador do processo
    message = f'1{SEPARATOR}{process_id}{SEPARATOR}'
    message = pad_message(message)

    # Envia a mensagem para o coordenador
    send_message_to_coordinator(message)

def create_release_message(process_id):
    # Cria uma mensagem de RELEASE com o código 3 e o identificador do processo
    message = f'3{SEPARATOR}{process_id}{SEPARATOR}'
    message = pad_message(message)

    # Envia a mensagem para o coordenador
    send_message_to_coordinator(message)

# Exemplo de utilização

# Inicia o processo criador
PROCESS_ID = '1000'
create_request_message(PROCESS_ID)
time.sleep(5)  # Simula um tempo de execução dentro da região crítica
create_release_message(PROCESS_ID)
PROCESS_ID = '2000'
create_request_message(PROCESS_ID)
time.sleep(5)  # Simula um tempo de execução dentro da região crítica
create_release_message(PROCESS_ID)