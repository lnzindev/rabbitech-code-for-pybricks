from base import *

CONFIGURADA = False  # Marque True quando cadastrar uma rota real.

def executar():

    print("TESTANDO AS DUAS GARRAS")

    garra_esquerda(180, 200)
    garra_direita(-180, 200)

    esperar(500)

    garra_esquerda(-180, 200)
    garra_direita(180, 200)

    return True
