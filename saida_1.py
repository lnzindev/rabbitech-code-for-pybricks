from base import andar, esperar, girar

def executar():

    print("SAIDA 1")

    if not andar(200, 60):
        print("SAIDA 1 INTERROMPIDA: FALHA AO AVANCAR")
        return False

    esperar(500)

    if not andar(-200, 60):
        print("SAIDA 1 INTERROMPIDA: FALHA AO RECUAR")
        return False

    esperar(500)

    if not girar(90, 45):
        print("SAIDA 1 INTERROMPIDA: FALHA NO GIRO")
        return False

    return True
