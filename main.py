# ==========================================
# RABBITECH - CONTROLADOR SEQUENCIAL
# Pybricks MicroPython 3.6.1
# Execute SOMENTE este arquivo.
# Os hashes são verificados no processo de publicação; o Hub não oferece
# leitura portátil dos arquivos-fonte instalados para validação runtime.
# ==========================================

from pybricks.parameters import Button
from pybricks.tools import wait

from base import hub, parar, esperar_imu

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

    # Esperar o botao ser solto
    while Button.LEFT in hub.buttons.pressed():
        wait(10)

    # Esperar um novo aperto
    while Button.LEFT not in hub.buttons.pressed():
        wait(10)

    # Esperar soltar novamente
    while Button.LEFT in hub.buttons.pressed():
        wait(10)


# ==========================================
# INICIAR CONTROLADOR
# ==========================================

esperar_imu()
parar()

numero = 1
falhou = False

# ==========================================
# EXECUTAR SAIDAS EM SEQUENCIA
# ==========================================

for item in SAIDAS:

    nome = item[0]
    programa = item[1]

    # Mostrar numero da saida
    hub.display.number(numero)

    print("AGUARDANDO SAIDA", numero, nome)

    # Esperar aperto do botao esquerdo
    esperar_botao_esquerdo()

    parar()

    print("EXECUTANDO:", nome)

    # Executar programacao individual
    resultado = programa()

    parar()

    # Verificar se ocorreu uma falha
    if resultado is False:

        hub.display.text("ERRO")

        print("SAIDA INTERROMPIDA:", nome)

        falhou = True
        break

    print("SAIDA CONCLUIDA:", nome)

    numero += 1


# ==========================================
# FINALIZAR CONTROLADOR
# ==========================================

parar()

if falhou:
    hub.display.text("ERRO")
    print("CONTROLADOR INTERROMPIDO")

else:
    hub.display.text("FIM")
    print("TODAS AS SAIDAS FINALIZADAS")