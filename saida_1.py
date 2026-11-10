from base import *

CONFIGURADA = False  # Marque True quando cadastrar uma rota real.

def executar():

    print("TESTANDO AS DUAS GARRAS")

    andar(780, 600)

    esperar(100)

    girar(-38, 80)

    andar(85, 100)

    esperar(500)
    garra_direita(360, 600)
    andar(-100, 200)
    #garra_esquerda(00, 600)

    garra_esquerda(60, 600)

    andar(-80, 200)

    girar(40, 80)

    andar (100,600)

    girar (20,600)


    garra_esquerda(-320,600)
    garra_esquerda(-90,600)


    girar(20,600)


    andar (80,200)
    return True
