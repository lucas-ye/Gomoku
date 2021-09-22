import pygame
import json
import socket
import numpy as np
import threading
import sys

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class myThread (threading.Thread):
    def __init__(self, IP_servidor, PORTA_servidor):
        threading.Thread.__init__(self)
        self.minhaVez = False
        # Criação de socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # IP e porta que o servidor deve aguardar a conexão
        self.sock.bind((IP_servidor, PORTA_servidor))

    def run(self):
        while True:
                data, self.addr = self.sock.recvfrom(1024)
                xi, yi = json.loads(data.decode("utf-8"))
                tabuleiro[yi, xi] = 1
                desenharTabuleiro()
                pygame.display.flip()
                self.minhaVez = True
    def send(self, lista):
        self.sock.sendto(json.dumps(lista).encode("utf-8"), self.addr)
        self.minhaVez = False

# transformar posicao em index do matriz
def positionToIndex(x, y):
    xdif = 0 if (x - 48 < 0) else x-48
    ydif = 0 if (y - 128 < 0) else y-128
    xdif = 504 if (x - 48 >= 522) else xdif
    ydif = 504 if (y - 128 >= 522) else ydif
    xi = round(xdif/36)
    yi = round(ydif/36)
    return (xi, yi)

# desenhar a peca
def desenharPeca(xi, yi, white):
    y = yi * 36 + 128
    x = xi * 36 + 48
    if white:
        pygame.draw.circle(screen, WHITE, (x, y), 16)
    else:
        pygame.draw.circle(screen, BLACK, (x, y), 16)

# desenhar a peca no cursor
def focus(xi, yi):
    y = yi * 36 + 128
    x = xi * 36 + 48
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, (255, 255, 255, 100), (x, y), 16)
    screen.blit(surface, (0, 0))

#desenhar tabuleiro e as pecas jogadas
def desenharTabuleiro():
    screen.fill((203,148,94))
    pygame.draw.rect(screen, BLACK,(45,125,510,510),3)
    for i in range(84, 552, 36):
        pygame.draw.line(screen, BLACK, (i, 125), (i, 635), 1)
    for i in range(164, 633, 36):
        pygame.draw.line(screen, BLACK, (45, i), (555, i), 1)
    status = np.where(tabuleiro == -1)
    for i in range(len(status[0])):
        desenharPeca(status[1][i], status[0][i], True)
    status = np.where(tabuleiro == 1)
    for i in range(len(status[0])):
        desenharPeca(status[1][i], status[0][i], False)
    fonteTexto = pygame.font.SysFont("comicsansms", 22)
    fraseTexto = fonteTexto.render("Jogador: Servidor", True, (226, 29, 44))
    screen.blit(fraseTexto, (45, 50))
#verificar se o jogo foi terminado
def verificar(jogador):
    #verificar linhas e colunas
    for i in range(15):
        linha = np.where(tabuleiro[i] == jogador)[0]
        if consecutivo(linha, len(linha)):
            return True
        coluna = np.where(tabuleiro[:, i] == jogador)[0]
        if consecutivo(coluna, len(coluna)):
            return True

    # obter diagonal principal
    for i in range(11):
        diagonal = []
        diagonal1 = []
        aux = i
        j = 0
        while j < 15 and aux < 15:
            diagonal.append(tabuleiro[j, aux])
            diagonal1.append(tabuleiro[aux, j])
            aux+=1
            j+=1
        diagonal = np.array(diagonal)
        diagonal = np.where(diagonal == jogador)[0]
        diagonal1 = np.array(diagonal1)
        diagonal1 = np.where(diagonal1 == jogador)[0]
        if consecutivo(diagonal, len(diagonal)):
            return True
        if consecutivo(diagonal1, len(diagonal1)):
            return True

    for i in range(4, 15):
        aux = i
        j = 0
        diagonal = []
        while aux != -1:
            diagonal.append(tabuleiro[j, aux])
            j+=1
            aux-=1
        diagonal = np.array(diagonal)
        diagonal = np.where(diagonal == jogador)[0]
        if consecutivo(diagonal, len(diagonal)):
            return True

    for i in range(1, 15):
        aux = i
        j = 14
        diagonal = []
        while j != i-1:
            diagonal.append(tabuleiro[aux, j])
            aux+=1
            j-=1
        diagonal = np.array(diagonal)
        diagonal = np.where(diagonal == jogador)[0]
        if consecutivo(diagonal, len(diagonal)):
            return True
    return False

def consecutivo(lista, tamanho):
    if tamanho < 5:
        return False
    count = 0
    result = 0
    for i in range(tamanho-1):
        count+=1
        result += (lista[i] - lista[i+1])
        if(count == 4):
            if result == -4:
                return True
            else:
                count = 0
                result = 0
    return False

def paginaFinal(ganhou):
    fonteTexto = pygame.font.SysFont("comicsansms", 30, bold = True)
    surface.fill((0, 0, 0, 50))
    if ganhou:
        info = fonteTexto.render("Vitória", True, (29, 226, 44))
    else:
        info = fonteTexto.render("Derrota", True, (226, 29, 44))
    surface.blit(info, (250, 300))
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    pygame.time.delay(5000)



IP = '192.168.0.6' # endereço IP do servidor
PORTA = 9998       # porta disponibilizada pelo servidor
thread1 = myThread(IP, PORTA)
thread1.daemon = True
thread1.start()
#inicializa as módulos dessa biblioteca.
pygame.init()

#Seta o tamanho da janela
screen = pygame.display.set_mode((600,700))
surface = pygame.Surface((600, 700),pygame.SRCALPHA)

#define um título na janela.
pygame.display.set_caption("Gomoku Servidor")
#situacao do tabuleiro
tabuleiro = np.zeros((15, 15))

desenharTabuleiro()
pygame.display.flip()
xi = -1
yi = -1
sair = False
while not sair:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sair = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (thread1.minhaVez):
                if(xi != -1 and yi != -1):
                    if tabuleiro[yi, xi] == 0:
                        tabuleiro[yi, xi] = -1
                        thread1.send([xi, yi])  # envia mensagem para cliente
                        desenharTabuleiro()
                        pygame.display.flip()

        if event.type == pygame.MOUSEMOTION and sair == False:
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]
            if 27 <= x <= 573 and 107 <= y <= 653:
                xi, yi = positionToIndex(x, y)
                desenharTabuleiro()
                focus(xi, yi)
                pygame.display.flip()
    if verificar(1):
        paginaFinal(False)
        break
    if verificar(-1):
        paginaFinal(True)
        break
#finalizar jogo
pygame.quit()
sys.exit()
