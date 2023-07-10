import random
import string
import threading
import time
import socket

class Processo(threading.Thread):
    def __init__(self, host='localhost', port=12345, r=10, k=5):
        threading.Thread.__init__(self)
        self.pid = ''.join(random.choices(string.digits, k=6))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.r = r  # número de vezes que o processo deve executar a região crítica
        self.k = k  # tempo de espera em segundos após escrever no arquivo

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
            arquivo.close
            time.sleep(3)

    def request(self):
        mensagem = self._criar_mensagem('1')
        self.client.send(mensagem.encode('utf-8'))

    def regiao_critica(self):
        # print('Processo', self.pid, 'esperando GRANT')
        resposta = self.client.recv(1024).decode('utf-8')  # Espera pela resposta do coordenador
        if resposta == 'GRANT':
            # print('Processo', self.pid, 'recebeu GRANT')
            # print('Processo', self.pid, 'entrou na região crítica')
            with open('resultado.txt', 'a') as arquivo:
                timestamp = time.time()
                hora_atual = time.strftime("%H:%M:%S", time.localtime(timestamp))
                milissegundos = int((timestamp - int(timestamp)) * 1000)
                linha = f'{self.pid} | {hora_atual}.{milissegundos:03}\n'
                arquivo.write(linha)
                time.sleep(self.k)
            #print('Processo', self.pid, 'saiu da região crítica')

    def release(self):
        mensagem = self._criar_mensagem('3')
        self.client.send(mensagem.encode('utf-8'))

    def _criar_mensagem(self, codigo):
        return f'{codigo}|{self.pid}|' + ''.join(['0' for _ in range(10 - len(codigo) - len(str(self.pid)) - 2)])

if __name__ == '__main__':
    num_processos = 10  # Número de processos a serem criados
    r = 10  # número de vezes que cada processo executará a região crítica
    k = 1  # tempo de espera em segundos após escrever no arquivo

    processos = []
    for _ in range(num_processos):
        processo = Processo(r=r, k=k)
        processos.append(processo)
        processo.start()

    for processo in processos:
        processo.join()
