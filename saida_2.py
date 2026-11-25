
from base import *

CONFIGURADA = True


def executar():

    print("TESTANDO AS DUAS GARRAS")
    
    andar(710,2000)
    girar(80,200)
    andar(80,2000)
    andar(30,2000)
    garra_esquerda(-95,2000)
    andar(-120,2000)
    girar(-120,2000)
    garra_direita(-160,2000)
    andar(120,2000)
    garra_direita(160,2000)

    parar_todos()

    print("SAIDA 1 CONCLUIDA")

    return True
