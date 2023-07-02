import random
import string
import threading
import time
import socket

class Processo(threading.Thread):
    def __init__(self, host='localhost', port=12345):
        threading.Thread.__init__(self)
        self.pid = ''.join(random.choices(string.digits, k=6))
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def run(self):
        self.create_file()
        self.request()
        self.regiao_critica()
        self.release()

    def create_file(self):
        with open('resultado.txt', 'w') as arquivo:
            arquivo.write('PID    | Hora Atual\n')
            arquivo.close
            time.sleep(3)

    def request(self):
        mensagem = self._criar_mensagem('1')
        self.client.send(mensagem.encode('utf-8'))

    def regiao_critica(self):
        print('Processo', self.pid, 'esperando GRANT')
        resposta = self.client.recv(1024).decode('utf-8')  # Espera pela resposta do coordenador
        if resposta == 'GRANT':
            print('Processo', self.pid, 'recebeu GRANT')
            print('Processo', self.pid, 'entrou na região crítica')
            with open('resultado.txt', 'a') as arquivo:
                timestamp = time.time()
                hora_atual = time.strftime("%H:%M:%S", time.localtime(timestamp))
                milissegundos = int((timestamp - int(timestamp)) * 1000)
                linha = f'{self.pid} | {hora_atual}.{milissegundos:03}\n'
                arquivo.write(linha)
                time.sleep(0)
                arquivo.close
            print('Processo', self.pid, 'saiu da região crítica')

    def release(self):
        mensagem = self._criar_mensagem('3')
        self.client.send(mensagem.encode('utf-8'))

    def _criar_mensagem(self, codigo):
        return f'{codigo}|{self.pid}|' + ''.join(['0' for _ in range(10 - len(codigo) - len(str(self.pid)) - 2)])

if __name__ == '__main__':
    num_processos = 100  # Número de processos a serem criados

    processos = []
    for _ in range(num_processos):
        processo = Processo()
        processos.append(processo)
        processo.start()

    for processo in processos:
        processo.join()
