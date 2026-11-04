from base import *

def executar():

    print("SAIDA 1")

    andar(200, 60)    # Frente
    esperar(500)

    andar(-200, 60)   # Ré
    esperar(500)

    girar(90, 45)     # Giro de 90 graus

    return True