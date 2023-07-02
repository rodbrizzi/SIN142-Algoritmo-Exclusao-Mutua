import random
import string
import threading
import time
import socket

class Processo(threading.Thread):
    def __init__(self, id, host='localhost', port=12345):
        threading.Thread.__init__(self)
        self.id = id
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def run(self):
        self.request()
        self.regiao_critica()
        self.release()

    def request(self):
        mensagem = self._criar_mensagem('1')
        self.client.send(mensagem.encode('utf-8'))

    def regiao_critica(self):
        print('Processo', self.id, 'esperando GRANT')
        resposta = self.client.recv(1024).decode('utf-8')  # Espera pela resposta do coordenador
        if resposta == 'GRANT':
            print('Processo', self.id, 'recebeu GRANT')
            print('Processo', self.id, 'entrou na região crítica')
            time.sleep(3)
            print('Processo', self.id, 'saiu da região crítica')

    def release(self):
        mensagem = self._criar_mensagem('3')
        self.client.send(mensagem.encode('utf-8'))

    def _criar_mensagem(self, codigo):
        return f'{codigo}|{self.id}|' + ''.join(['0' for _ in range(10 - len(codigo) - len(str(self.id)) - 2)])

if __name__ == '__main__':
    processo1 = Processo(10)
    processo2 = Processo(20)
    processo1.start()
    processo2.start()
