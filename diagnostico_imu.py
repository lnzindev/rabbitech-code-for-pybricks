# ==========================================
# RABBITECH - DIAGNOSTICO DE ESCALA DA IMU
# Pybricks MicroPython 3.6.1 / SPIKE Prime
#
# Objetivo:
# Medir quantos graus BRUTOS a IMU informa quando o
# robo completa uma volta fisica de 360 graus.
#
# IMPORTANTE:
# - Deixe o robo em uma superficie plana.
# - Nao mova as rodas/motores durante a medicao.
# - Gire o robo inteiro lentamente, sem inclinar.
# - Uma volta deve ser o mais proximo possivel de 360 graus.
# - Este programa NAO altera a calibracao automaticamente.
# ==========================================

from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Button
from pybricks.tools import wait

hub = PrimeHub()
hub.system.set_stop_button(None)

print("DIAGNOSTICO DA IMU - RABBITECH")
print("Aguardando calibracao...")
while not hub.imu.ready():
    wait(20)

print("IMU PRONTA")
print("CONFIGURACAO ATUAL:", hub.imu.settings())
print("Deixe o robo plano e parado.")
print("Pressione LEFT para iniciar a medicao.")

# Aguarda primeiro toque.
while Button.LEFT not in hub.buttons.pressed():
    if Button.CENTER in hub.buttons.pressed():
        hub.system.set_stop_button(Button.CENTER)
        raise SystemExit
    wait(10)

while Button.LEFT in hub.buttons.pressed():
    wait(10)

hub.imu.reset_heading(0)
bruto_inicial = hub.imu.rotation(-Axis.Z, calibrated=False)

print("MEDICAO INICIADA")
print("Gire o robo MANUALMENTE uma volta completa de 360 graus.")
print("Mantenha-o plano. Pressione LEFT ao terminar.")

while Button.LEFT not in hub.buttons.pressed():
    if Button.CENTER in hub.buttons.pressed():
        hub.system.set_stop_button(Button.CENTER)
        raise SystemExit
    wait(10)

bruto_final = hub.imu.rotation(-Axis.Z, calibrated=False)
heading_final = hub.imu.heading()
bruto_volta = bruto_final - bruto_inicial

print("==============================")
print("RESULTADO DA CALIBRACAO")
print("ROTACAO BRUTA:", bruto_volta)
print("HEADING CALIBRADO:", heading_final)
print("VALOR ATUAL DE HEADING_CORRECTION:", hub.imu.settings()[2])
print("SUGESTAO: repetir a medicao 3 vezes e usar a media.")
print("NAO aplique o valor se a volta fisica nao foi exatamente 360 graus.")
print("==============================")
print("Envie todos os valores exibidos.")
hub.system.set_stop_button(Button.CENTER)
