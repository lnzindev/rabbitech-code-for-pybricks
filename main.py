# ==========================================
# RABBITECH - CONTROLADOR DE COMPETICAO
# Pybricks MicroPython 3.6.1
#
# Uma rodada possui 150 segundos totais.
# Falha de uma saida nao encerra as outras.
# CENTER e monitorado pelo proprio programa.
# ==========================================

from pybricks.parameters import Button
from pybricks.tools import wait

from base import (
    hub,
    parar,
    esperar_imu,
    iniciar_competicao,
    verificar_competicao,
    tempo_restante,
    finalizar_competicao,
    solicitar_parada,
)

from saida_1 import executar as programa1
from saida_2 import executar as programa2
from saida_3 import executar as programa3
from saida_4 import executar as programa4
from saida_5 import executar as programa5
from saida_6 import executar as programa6
from saida_7 import executar as programa7
from saida_8 import executar as programa8


# ==========================================
# CONFIGURACAO DAS SAIDAS
#
# True  = executar
# False = ignorar
# ==========================================

SAIDAS = [
    ("SAIDA 1", programa1, True),
    ("SAIDA 2", programa2, False),
    ("SAIDA 3", programa3, False),
    ("SAIDA 4", programa4, False),
    ("SAIDA 5", programa5, False),
    ("SAIDA 6", programa6, False),
    ("SAIDA 7", programa7, False),
    ("SAIDA 8", programa8, False),
]


def esperar_inicio():
    # Aguarda um novo pressionamento de LEFT.
    while Button.LEFT not in hub.buttons.pressed():
        if Button.CENTER in hub.buttons.pressed():
            solicitar_parada()
            return False

        wait(10)

    # Aguarda LEFT ser solto.
    while Button.LEFT in hub.buttons.pressed():
        if Button.CENTER in hub.buttons.pressed():
            solicitar_parada()
            return False

        wait(10)

    return True


def esperar_proxima_saida():
    # Aguarda LEFT ser solto.
    while Button.LEFT in hub.buttons.pressed():
        if not verificar_competicao():
            return False

        wait(10)

    # Aguarda um novo pressionamento.
    while Button.LEFT not in hub.buttons.pressed():
        if not verificar_competicao():
            return False

        wait(10)

    # Aguarda a liberacao do botao.
    while Button.LEFT in hub.buttons.pressed():
        if not verificar_competicao():
            return False

        wait(10)

    return verificar_competicao()


def executar_controlador():

    if not esperar_imu():
        return False

    parar()
    hub.display.char("R")

    if not esperar_inicio():
        return False

    iniciar_competicao()

    primeira_saida = True

    for nome, programa, configurada in SAIDAS:

        if not verificar_competicao():
            break

        if not configurada:
            print(nome, "NAO CONFIGURADA - IGNORADA")
            continue

        if not primeira_saida:
            print("AGUARDANDO PARTIDA:", nome)

            if not esperar_proxima_saida():
                break

        primeira_saida = False

        if not verificar_competicao():
            break

        numero = int(nome[-1])

        hub.display.number(numero)
        print("EXECUTANDO:", nome)

        try:
            resultado = programa()

            if resultado is False:
                print(nome, "RETORNOU FALHA.")
            else:
                print(nome, "CONCLUIDA.")

        except Exception as erro:
            print("ERRO NA", nome, ":", erro)
            print("TENTANDO CONTINUAR A RODADA.")

        finally:
            parar()

        if not verificar_competicao():
            break

    # Aguarda o fim oficial da rodada.
    if verificar_competicao():
        print("ROTAS FINALIZADAS. AGUARDANDO FIM DA RODADA.")

        while verificar_competicao():
            wait(10)

    return True


# ==========================================
# EXECUCAO E ENCERRAMENTO SEGURO
# ==========================================

try:
    executar_controlador()

except Exception as erro:
    print("ERRO NO CONTROLADOR:", erro)
    solicitar_parada()

finally:
    # Captura o tempo antes de finalizar a competicao.
    restante = tempo_restante()

    parar()
    finalizar_competicao()

    if restante <= 0:
        hub.display.char("F")
    else:
        hub.display.char("S")
