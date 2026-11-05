from base import *

def executar():

    print("TESTANDO AS DUAS GARRAS")

    garra_esquerda(180, 200)
    garra_direita(-180, 200)

    esperar(500)

    garra_esquerda(-180, 200)
    garra_direita(180, 200)

    return True
