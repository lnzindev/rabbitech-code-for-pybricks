from base import *

CONFIGURADA = False  # Marque True quando cadastrar uma rota real.

def executar():

    print("TESTANDO AS DUAS GARRAS")

    andar(780, 600)

    esperar(100)

    girar(-48, 80)

    andar(100, 100)

    esperar(500)
    garra_direita(256, 200)
    garra_esquerda(200, 200)
    andar(-150, 200)
    giraR(90, 80)

    return True
