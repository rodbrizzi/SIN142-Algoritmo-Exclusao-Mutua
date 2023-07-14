import random
import string
import threading
import time
import socket
from datetime import datetime
import sys

# Endereço IP e porta do servidor
HOST = 'localhost'
PORT = 12345

class Processo(threading.Thread):
    def __init__(self, host=HOST, port=PORT, r=10, k=5):
        threading.Thread.__init__(self)
        # Gera um identificador de processo único (PID)
        self.pid = ''.join(random.choices(string.digits, k=6))
        self.r = r  # Define quantas vezes este processo deve acessar a região crítica
        self.k = k  # Define quanto tempo (em segundos) este processo deve aguardar após acessar a região crítica
        try:
            # Cria uma conexão socket com o servidor
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
        except socket.error as e:
            print("Erro de conexão: ", str(e))
            sys.exit(1)
    def run(self):
        try:
            # Inicia o arquivo de saída
            self.create_file()
            # O processo executa sua rotina r vezes
            for _ in range(self.r):
                self.request()  # O processo solicita acesso à região crítica
                self.regiao_critica()  # O processo acessa a região crítica
                self.release()  # O processo libera o acesso à região crítica
        except socket.error as e:
            print("Erro de conexão: ", str(e))
            sys.exit(1)
        finally:
            # Fecha a conexão socket quando terminar
            self.client.close()

    def create_file(self):
        # Cria um arquivo chamado 'resultado.txt' para registrar as atividades do processo
        with open('resultado.txt', 'w') as arquivo:
            arquivo.write('PID    | Hora Atual\n')
            time.sleep(3)

    def request(self):
        # Envia uma solicitação ao servidor para acessar a região crítica
        try:
            mensagem = self._criar_mensagem('1')
            self.client.send(mensagem.encode('utf-8'))
        except socket.error as e:
            print("Erro de conexão: ", str(e))
            sys.exit(1)

    def regiao_critica(self):
        # Aguarda a resposta do coordenador para acessar a região crítica
        try:
            resposta = self.client.recv(1024).decode('utf-8')  
            if resposta.startswith('2'):  # Se a resposta começar com '2', então acesso é concedido (GRANT)
                with open('resultado.txt', 'a') as arquivo:
                    timestamp = time.time()
                    hora_atual = time.strftime("%H:%M:%S", time.localtime(timestamp))
                    milissegundos = int((timestamp - int(timestamp)) * 1000)
                    linha = f'{self.pid} | {hora_atual}.{milissegundos:03}\n'
                    arquivo.write(linha)
                    time.sleep(self.k)  # Aguarda k segundos antes de liberar a região crítica
        except socket.error as e:
            print("Erro de conexão: ", str(e))
            sys.exit(1)

    def release(self):
        # Envia uma mensagem ao servidor para liberar a região crítica
        try:
            mensagem = self._criar_mensagem('3')
            self.client.send(mensagem.encode('utf-8'))
        except socket.error as e:
            print("Erro de conexão: ", str(e))
            sys.exit(1)

    def _criar_mensagem(self, codigo):
        # Cria uma mensagem para ser enviada ao servidor
        return f'{codigo}|{self.pid}|'.ljust(10, '0')

def get_integer_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

def main():
    try:
        n = get_integer_input("\nDigite a quantidade de processos a serem criados: ")  
        r = get_integer_input("\nDigite quantas vezes cada processo deve acessar a região crítica: ")
        k = get_integer_input("\nDigite o tempo em segundos para cada execução na região crítica: ")  
        print("\nExecutando o programa...")

        # Cria n processos
        processos = [Processo(r=r, k=k) for _ in range(n)]

        # Inicia todos os processos
        for processo in processos:
            processo.start()

        # Aguarda todos os processos terminarem
        for processo in processos:
            processo.join()

        # Escreve os parâmetros do experimento no arquivo de saída
        with open('resultado.txt', 'a') as arquivo:
            arquivo.write(f'\nQuantidade de processos(n): {n}\n')
            arquivo.write(f'Quantidade de vezes que cada processo executou a região crítica(r): {r}\n')
            arquivo.write(f'Tempo definido em segundos para cada execução na região crítica(k): {k}\n')

        # Calcula o tempo total para a geração do arquivo 'resultado.txt'
        with open('resultado.txt', 'r') as f:
            lines = f.readlines()
            first_line_time = lines[1].split('|')[1].strip()  
            last_line_time = lines[-5].split('|')[1].strip() 

            FMT = '%H:%M:%S.%f'
            tdelta = datetime.strptime(last_line_time, FMT) - datetime.strptime(first_line_time, FMT)

        with open('resultado.txt', 'a') as arquivo:
            arquivo.write(f"\nTempo total para geração do arquivo 'resultado.txt': {tdelta.total_seconds()} segundos")
        
        print("Execução do programa concluída com sucesso.")
    except socket.error as e:
        print("Erro de conexão: ", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
