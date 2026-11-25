
# ==========================================
# RABBITECH - CONTROLADOR SEQUENCIAL
# Pybricks MicroPython 3.6.1
# ==========================================

from pybricks.parameters import Button
from pybricks.tools import wait

from base import (
    hub,
    parar,
    parar_todos,
    esperar_imu,
    verificar_competicao
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
# LISTA DAS OITO SAIDAS
# ==========================================

SAIDAS = [
    ("SAIDA 1", programa1),
    ("SAIDA 2", programa2),
    ("SAIDA 3", programa3),
    ("SAIDA 4", programa4),
    ("SAIDA 5", programa5),
    ("SAIDA 6", programa6),
    ("SAIDA 7", programa7),
    ("SAIDA 8", programa8),
]


# ==========================================
# ESPERAR BOTAO ESQUERDO
# ==========================================

def esperar_botao_esquerdo():

    # Esperar botao soltar
    while Button.LEFT in hub.buttons.pressed():

        if not verificar_competicao():
            return False

        wait(10)

    # Esperar novo aperto
    while Button.LEFT not in hub.buttons.pressed():

        if not verificar_competicao():
            return False

        wait(10)

    # Esperar soltar novamente
    while Button.LEFT in hub.buttons.pressed():

        if not verificar_competicao():
            return False

        wait(10)

    return verificar_competicao()


# ==========================================
# INICIAR CONTROLADOR
# ==========================================

print("RABBITECH - INICIANDO")



if not esperar_imu():

    parar_todos()

    hub.display.text("IMU ERRO")

    print("ERRO NA INICIALIZACAO DA IMU")

else:

    parar()

    numero = 1
    falhou = False
    interrompido = False

    # ======================================
    # EXECUTAR SAIDAS EM SEQUENCIA
    # ======================================

    for nome, programa in SAIDAS:

        if not verificar_competicao():
            interrompido = True
            break

        hub.display.number(numero)

        print("AGUARDANDO:", nome)

        if not esperar_botao_esquerdo():

            interrompido = True
            break

        parar()

        if not verificar_competicao():

            interrompido = True
            break

        print("EXECUTANDO:", nome)

        try:

            resultado = programa()

        except Exception as erro:

            print("ERRO NA", nome, ":", erro)

            resultado = False

        parar()

        if resultado is False:

            hub.display.text("ERRO")

            print("SAIDA INTERROMPIDA:", nome)

            falhou = True
            break

        if not verificar_competicao():

            interrompido = True
            break

        print("SAIDA CONCLUIDA:", nome)

        numero += 1

    # ======================================
    # FINALIZAR CONTROLADOR
    # ======================================

    parar_todos()

    if falhou:

        hub.display.text("ERRO")

        print("CONTROLADOR INTERROMPIDO POR FALHA")

    elif interrompido:

        

        print("CONTROLADOR INTERROMPIDO")

    else:

        hub.display.text("FIM")

        print("TODAS AS SAIDAS FINALIZADAS")
