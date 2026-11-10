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

from saida_1 import executar as programa1, CONFIGURADA as ativa1
from saida_2 import executar as programa2, CONFIGURADA as ativa2
from saida_3 import executar as programa3, CONFIGURADA as ativa3
from saida_4 import executar as programa4, CONFIGURADA as ativa4
from saida_5 import executar as programa5, CONFIGURADA as ativa5
from saida_6 import executar as programa6, CONFIGURADA as ativa6
from saida_7 import executar as programa7, CONFIGURADA as ativa7
from saida_8 import executar as programa8, CONFIGURADA as ativa8


SAIDAS = [
    ("SAIDA 1", programa1, ativa1),
    ("SAIDA 2", programa2, ativa2),
    ("SAIDA 3", programa3, ativa3),
    ("SAIDA 4", programa4, ativa4),
    ("SAIDA 5", programa5, ativa5),
    ("SAIDA 6", programa6, ativa6),
    ("SAIDA 7", programa7, ativa7),
    ("SAIDA 8", programa8, ativa8),
]


def esperar_inicio():
    # O primeiro toque em LEFT inicia o cronometro oficial.
    while Button.LEFT not in hub.buttons.pressed():
        if Button.CENTER in hub.buttons.pressed():
            solicitar_parada()
            return False
        wait(10)

    while Button.LEFT in hub.buttons.pressed():
        if Button.CENTER in hub.buttons.pressed():
            solicitar_parada()
            return False
        wait(10)

    return True


def esperar_proxima_saida():
    # LEFT dispara a proxima saida cadastrada.
    # O tempo da rodada continua contando enquanto aguarda.
    while Button.LEFT in hub.buttons.pressed():
        if not verificar_competicao():
            return False
        wait(10)

    while Button.LEFT not in hub.buttons.pressed():
        if not verificar_competicao():
            return False
        wait(10)

    while Button.LEFT in hub.buttons.pressed():
        if not verificar_competicao():
            return False
        wait(10)

    return verificar_competicao()


# ==========================================
# PREPARACAO
# ==========================================

esperar_imu()
parar()
hub.display.text("READY")

# ==========================================
# EXECUCAO DA RODADA
# ==========================================

if esperar_inicio():
    iniciar_competicao()
    primeira_saida = True

    for item in SAIDAS:
        nome = item[0]
        programa = item[1]
        configurada = item[2]

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

        hub.display.text(str(nome[-1]))
        print("EXECUTANDO:", nome)

        resultado = programa()
        parar()

        # Uma falha local nao encerra a rodada.
        # O proximo roteiro continua disponivel enquanto houver tempo.
        if not verificar_competicao():
            break

        if resultado is False:
            print(nome, "TEVE FALHA LOCAL. RODADA CONTINUA.")
        else:
            print(nome, "CONCLUIDA.")

    # Nao repetir automaticamente rotas ja executadas.
    # Depois das saidas cadastradas, manter a rodada ativa ate 150 s
    # ou ate o operador pressionar CENTER.
    if verificar_competicao():
        print("ROTAS CADASTRADAS FINALIZADAS. AGUARDANDO FIM DA RODADA.")
        while verificar_competicao():
            wait(10)


# ==========================================
# ENCERRAMENTO CONTROLADO
# ==========================================

restante = tempo_restante()

if restante <= 0:
    hub.display.text("FIM")
else:
    hub.display.text("STOP")

finalizar_competicao()
