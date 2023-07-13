import random
import string
import threading
import time
import socket
from datetime import datetime

class Processo(threading.Thread):
    def __init__(self, host='localhost', port=12345, r=10, k=5):
        threading.Thread.__init__(self)
        self.pid = ''.join(random.choices(string.digits, k=6))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.r = r  # número de vezes que o processo deve executar a região crítica
        self.k = k  # tempo de espera em segundos após escrever no arquivo
        self.tempo_na_regiao_critica = 0
        self.start_time = None
        self.end_time = None

    def run(self):
        self.create_file()
        for _ in range(self.r):
            self.request()
            self.regiao_critica()
            self.release()
        self.client.close()

    def create_file(self):
        with open('resultado.txt', 'w') as arquivo:
            arquivo.write('PID    | Hora Atual\n')
            arquivo.close()
            time.sleep(3)

    def request(self):
        mensagem = self._criar_mensagem('1')
        self.client.send(mensagem.encode('utf-8'))

    def regiao_critica(self):
        resposta = self.client.recv(1024).decode('utf-8')  # Espera pela resposta do coordenador
        if resposta.startswith('2'):  # GRANT
            self.start_time = self.start_time or time.time()
            start_time = time.time()
            with open('resultado.txt', 'a') as arquivo:
                timestamp = time.time()
                hora_atual = time.strftime("%H:%M:%S", time.localtime(timestamp))
                milissegundos = int((timestamp - int(timestamp)) * 1000)
                linha = f'{self.pid} | {hora_atual}.{milissegundos:03}\n'
                arquivo.write(linha)
                time.sleep(self.k)
            self.tempo_na_regiao_critica += time.time() - start_time
            self.end_time = time.time()

    def release(self):
        mensagem = self._criar_mensagem('3')
        self.client.send(mensagem.encode('utf-8'))

    def _criar_mensagem(self, codigo):
        return f'{codigo}|{self.pid}|' + ''.join(['0' for _ in range(10 - len(codigo) - len(str(self.pid)) - 2)])

if __name__ == '__main__':
    n = 64 # Número de processos a serem criados
    r = 100  # número de vezes que cada processo executará a região crítica
    k = 1  # tempo de espera em segundos após escrever no arquivo

    processos = []
    for _ in range(n):
        processo = Processo(r=r, k=k)
        processos.append(processo)
        processo.start()

    for processo in processos:
        processo.join()

    with open('resultado.txt', 'a') as arquivo:
        arquivo.write(f'\nQuantidade de processos(n): {n}\n')
        arquivo.write(f'Quantidade de vezes que cada processo executou a região crítica(r): {r}\n')
        arquivo.write(f'Tempo definido em segundos para cada execução na região crítica(k): {k}\n')

    # Calculating the time from the file
    with open('resultado.txt', 'r') as f:
        lines = f.readlines()
        first_line_time = lines[1].split('|')[1].strip()  # First timestamp
        last_line_time = lines[-5].split('|')[1].strip()  # Last timestamp

        FMT = '%H:%M:%S.%f'
        tdelta = datetime.strptime(last_line_time, FMT) - datetime.strptime(first_line_time, FMT)

    with open('resultado.txt', 'a') as arquivo:
        arquivo.write(f"\nTempo total para geração do arquivo 'resultado.txt': {tdelta.total_seconds()} segundos")
