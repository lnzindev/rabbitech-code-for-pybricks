
# ==========================================
# RABBITECH - AUTOPILOT V3.2
# Pybricks MicroPython 3.6.1
#
# MOTORES:
# C = GARRA ESQUERDA
# D = GARRA DIREITA
# E = TRACAO ESQUERDA
# F = TRACAO DIREITA
#
# RODAS: 56 MM
# MEMORIA ADAPTATIVA
# VELOCIDADE E ANGULOS PERSONALIZAVEIS
# ==========================================

from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import wait, StopWatch
import memoria as memoria_store

# ==========================================
# INICIALIZACAO
# ==========================================

hub = PrimeHub()
hub.system.set_stop_button(None)

mL = Motor(Port.E, Direction.COUNTERCLOCKWISE)
mR = Motor(Port.F, Direction.CLOCKWISE)

garra_esq = Motor(Port.C)
garra_dir = Motor(Port.D)

DIAMETRO_RODA = 56

# ==========================================
# CONFIGURACOES PERSONALIZAVEIS
# ==========================================

VELOCIDADE_ANDAR = 60
VELOCIDADE_GIRAR = 45
VELOCIDADE_GARRA = 300

VELOCIDADE_MINIMA = 10
VELOCIDADE_MAXIMA = 100

VELOCIDADE_INICIAL = 45
VELOCIDADE_FINAL = 30

ANGULO_GARRA_ABERTA = 90
ANGULO_GARRA_FECHADA = 90

# ==========================================
# INTELIGENCIA ADAPTATIVA
# ==========================================

KP_G = 1.4
KI_G = 0.12
KD_G = 0.006

MAX_CORRECAO = 16
MAX_MEMORIA = 7

memoria_frente = 0.0
memoria_re = 0.0

movimentos_concluidos = 0
movimentos_falhos = 0

# ==========================================
# CONTROLE DA RODADA DE COMPETICAO
# ==========================================

TEMPO_COMPETICAO = 150000
_relogio_competicao = None
_competicao_ativa = False
_parada_solicitada = False
_motivo_fim = None


def iniciar_competicao():
    global _relogio_competicao, _competicao_ativa
    global _parada_solicitada, _motivo_fim

    _relogio_competicao = StopWatch()
    _competicao_ativa = True
    _parada_solicitada = False
    _motivo_fim = None

    print("RODADA INICIADA: 150 SEGUNDOS")
    return True


def solicitar_parada():
    global _parada_solicitada, _motivo_fim

    _parada_solicitada = True
    _motivo_fim = "PARADA SOLICITADA"

    print("PARADA MANUAL SOLICITADA")
    return True


def verificar_competicao():
    global _parada_solicitada, _motivo_fim

    if _parada_solicitada:
        return False

    if Button.CENTER in hub.buttons.pressed():
        _parada_solicitada = True
        _motivo_fim = "BOTAO CENTRAL"
        print("RODADA INTERROMPIDA PELO BOTAO CENTRAL")
        return False

    if not _competicao_ativa:
        return True

    if _motivo_fim == "TEMPO ESGOTADO":
        return False

    if _relogio_competicao.time() >= TEMPO_COMPETICAO:
        _motivo_fim = "TEMPO ESGOTADO"
        print("TEMPO OFICIAL ESGOTADO")
        return False

    return True


def tempo_restante():
    if not _competicao_ativa or _relogio_competicao is None:
        return TEMPO_COMPETICAO

    return max(0, TEMPO_COMPETICAO - _relogio_competicao.time())


def esperar_controlado(tempo_ms):
    restante = max(0, int(tempo_ms))

    while restante > 0:
        if not verificar_competicao():
            return False

        intervalo = min(10, restante)
        wait(intervalo)
        restante -= intervalo

    return verificar_competicao()


def finalizar_competicao():
    global _competicao_ativa

    parar()
    parar_garras()
    _competicao_ativa = False
    hub.system.set_stop_button(Button.CENTER)

    print("FIM DA RODADA:", _motivo_fim)
    return True


# ==========================================
# CONFIGURACAO DOS GIROS
# ==========================================

KP_T = 1.5
KD_T = 0.3

TOLERANCIA_GIRO = 3.0
TIMEOUT_GIRO = 8000

POTENCIA_MIN_GIRO = 25
POTENCIA_MAX_GIRO = 40
SINAL_GIRO = 1

# ==========================================
# MEMORIA PERMANENTE
# ==========================================

def salvar_aprendizado():
    return memoria_store.salvar(
        hub, memoria_frente, memoria_re,
        movimentos_concluidos, movimentos_falhos
    )


def carregar_aprendizado():
    global memoria_frente, memoria_re
    global movimentos_concluidos, movimentos_falhos

    (
        memoria_frente,
        memoria_re,
        movimentos_concluidos,
        movimentos_falhos
    ) = memoria_store.carregar(hub)

    return True


def registrar_falha():
    global movimentos_falhos

    movimentos_falhos = min(65535, movimentos_falhos + 1)

    print("MOVIMENTO FALHOU")
    salvar_aprendizado()


def registrar_sucesso():
    global movimentos_concluidos

    movimentos_concluidos = min(65535, movimentos_concluidos + 1)

    print("MOVIMENTO CONCLUIDO")
    salvar_aprendizado()


carregar_aprendizado()


# ==========================================
# FUNCOES BASICAS
# ==========================================

def limitar(valor, minimo=-100, maximo=100):
    return max(minimo, min(maximo, valor))


def esperar_imu():

    while not hub.imu.ready():
        if not verificar_competicao():
            return False

        wait(10)

    return verificar_competicao()


def parar():
    mL.hold()
    mR.hold()


def distancia_percorrida():
    return (
        abs(mL.angle()) + abs(mR.angle())
    ) / 2


def velocidade_rampa(
    atual,
    total,
    inicio,
    alvo,
    final,
    subida,
    descida
):

    restante = total - atual

    if atual < subida and subida > 0:
        velocidade = (
            inicio + (alvo - inicio) * atual / subida
        )

    elif restante < descida and descida > 0:
        velocidade = (
            final + (alvo - final)
            * max(0, restante) / descida
        )

    else:
        velocidade = alvo

    return limitar(velocidade, 0, 100)


# ==========================================
# CONTROLE DAS GARRAS
# ==========================================

def mover_motor_supervisionado(motor, angulo, velocidade):

    if not verificar_competicao():
        return False

    motor.run_angle(
        velocidade,
        angulo,
        then=Stop.HOLD,
        wait=False
    )

    while not motor.done():

        if not verificar_competicao():
            motor.hold()
            return False

        wait(10)

    return verificar_competicao()


def garra_esquerda(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor_supervisionado(
        garra_esq, angulo, velocidade
    )


def garra_direita(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor_supervisionado(
        garra_dir, angulo, velocidade
    )


def abrir_garras():

    if not garra_esquerda(-ANGULO_GARRA_ABERTA):
        return False

    if not garra_direita(ANGULO_GARRA_ABERTA):
        return False

    return True


def fechar_garras():

    if not garra_esquerda(ANGULO_GARRA_FECHADA):
        return False

    if not garra_direita(-ANGULO_GARRA_FECHADA):
        return False

    return True


def parar_garras():
    garra_esq.hold()
    garra_dir.hold()
    return True


# ==========================================
# CALCULO DOS GIROS
# ==========================================

def calcular_giro(erro, ultimo_erro, velocidade):

    variacao = erro - ultimo_erro

    correcao = (
        erro * KP_T + variacao * KD_T
    )

    correcao = limitar(
        correcao,
        -velocidade,
        velocidade
    )

    minimo = (
        min(9, velocidade)
        if abs(erro) > 10
        else min(4, velocidade)
    )

    if correcao > 0:
        correcao = max(minimo, correcao)

    elif correcao < 0:
        correcao = min(-minimo, correcao)

    else:
        correcao = minimo if erro > 0 else -minimo

    return correcao


# ==========================================
# GIRO COM DUAS RODAS
# ==========================================

def giro_interno(angulo, velocidade=45):

    if abs(angulo) < 0.1:
        parar()
        return True

    parar()

    if not esperar_imu():
        return False

    if not esperar_controlado(200):
        return False

    # Zera a referencia da IMU com o robo parado.
    hub.imu.reset_heading(0)

    if not esperar_controlado(50):
        return False

    limite_potencia = limitar(
        abs(velocidade),
        POTENCIA_MIN_GIRO,
        POTENCIA_MAX_GIRO
    )

    # ETAPA 1: giro principal com reducao de potencia.
    relogio = StopWatch()
    ultimo_tempo = relogio.time()
    ultimo_heading = hub.imu.heading()
    estavel = 0

    while relogio.time() < TIMEOUT_GIRO:

        if not verificar_competicao():
            parar()
            return False

        wait(10)

        agora = relogio.time()
        heading = hub.imu.heading()
        erro = angulo - heading

        dt = (agora - ultimo_tempo) / 1000
        if dt <= 0:
            dt = 0.01

        taxa = (heading - ultimo_heading) / dt
        ultimo_tempo = agora
        ultimo_heading = heading

        restante = abs(erro)
        sentido_erro = 1 if erro > 0 else -1
        taxa_na_direcao = taxa * sentido_erro

        # Ao entrar na faixa, segura e deixa a inercia diminuir.
        if restante <= TOLERANCIA_GIRO:
            parar()

            if abs(taxa) <= 8:
                estavel += 1
            else:
                estavel = 0

            if estavel >= 3:
                break

            continue

        estavel = 0

        if restante > 35:
            potencia = limite_potencia
        elif restante > 15:
            potencia = max(
                POTENCIA_MIN_GIRO,
                int(limite_potencia * 0.75)
            )
        elif restante > 5:
            potencia = max(
                POTENCIA_MIN_GIRO,
                int(limite_potencia * 0.60)
            )
        else:
            potencia = POTENCIA_MIN_GIRO

        # Frenagem antecipada quando a velocidade angular esta alta.
        if taxa_na_direcao > 180 and restante < 45:
            comando = -POTENCIA_MIN_GIRO * sentido_erro
        elif taxa_na_direcao > 100 and restante < 35:
            comando = sentido_erro * min(potencia, 7)
        else:
            comando = sentido_erro * potencia

        comando = limitar(
            comando * SINAL_GIRO,
            -limite_potencia,
            limite_potencia
        )

        mL.dc(int(comando))
        mR.dc(int(-comando))

    # ETAPA 2: para, espera a inercia e mede o erro real.
    parar()

    if not esperar_controlado(150):
        return False

    angulo_real = hub.imu.heading()
    erro_final = angulo - angulo_real

    print("GIRO PRINCIPAL:", angulo_real)
    print("ERRO ANTES DA CORRECAO:", erro_final)

    if not verificar_competicao():
        return False

    # Nao tenta corrigir um erro grande com pequenos pulsos.
    LIMITE_ERRO_CORRECAO = 12.0
    TOLERANCIA_FINAL_GIRO = 1.5
    MAX_TENTATIVAS_CORRECAO = 5
    TEMPO_MAX_CORRECAO = 1000

    relogio_correcao = StopWatch()
    tentativas = 0

    while (
        abs(erro_final) > TOLERANCIA_FINAL_GIRO
        and abs(erro_final) <= LIMITE_ERRO_CORRECAO
        and tentativas < MAX_TENTATIVAS_CORRECAO
        and relogio_correcao.time() < TEMPO_MAX_CORRECAO
    ):

        if not verificar_competicao():
            parar()
            return False

        tentativas += 1

        sentido_erro = 1 if erro_final > 0 else -1
        restante = abs(erro_final)

        # Controle proporcional limitado: erro menor gera pulso menor.
        potencia_correcao = limitar(
            int(22 + restante * 1.1),
            POTENCIA_MIN_GIRO,
            33
        )

        pulso_ms = limitar(
            int(12 + restante * 7),
            15,
            85
        )

        comando = int(
            sentido_erro * potencia_correcao * SINAL_GIRO
        )

        mL.dc(comando)
        mR.dc(-comando)

        if not esperar_controlado(pulso_ms):
            parar()
            return False

        parar()

        # Aguarda a mecanica assentar antes de medir novamente.
        if not esperar_controlado(110):
            return False

        angulo_real = hub.imu.heading()
        erro_final = angulo - angulo_real

        print(
            "CORRECAO", tentativas,
            "ANGULO:", angulo_real,
            "ERRO:", erro_final
        )

    parar()

    if not esperar_controlado(100):
        return False

    # Medicao final independente da ultima tentativa.
    angulo_real = hub.imu.heading()
    erro_final = angulo - angulo_real

    print("GIRO ALVO:", angulo)
    print("GIRO REAL:", angulo_real)
    print("ERRO FINAL:", erro_final)

    if not verificar_competicao():
        return False

    if abs(erro_final) > TOLERANCIA_FINAL_GIRO:
        print("GIRO NAO ATINGIU A PRECISAO FINAL")
        registrar_falha()
        return False

    print("GIRO APROVADO COM REFINAMENTO IMU")
    registrar_sucesso()
    return True


# ==========================================
# GIRO COM UMA RODA
# ==========================================

def giro_uma_roda_interno(angulo, velocidade=45):

    parar()

    if not esperar_imu():
        return False

    hub.imu.reset_heading(0)

    ultimo_erro = 0
    relogio = StopWatch()
    concluiu = False

    if angulo > 0:
        mR.hold()
    else:
        mL.hold()

    while relogio.time() < TIMEOUT_GIRO:

        if not verificar_competicao():
            parar()
            return False

        erro = angulo - hub.imu.heading()

        if abs(erro) < TOLERANCIA_GIRO:
            concluiu = True
            break

        correcao = calcular_giro(
            erro,
            ultimo_erro,
            velocidade
        )

        if angulo > 0:
            mL.dc(correcao)
        else:
            mR.dc(-correcao)

        ultimo_erro = erro
        wait(5)

    parar()

    if not verificar_competicao():
        return False

    if not concluiu:
        print("ERRO NO GIRO DE UMA RODA")
        registrar_falha()
        return False

    registrar_sucesso()
    return True


# ==========================================
# MOVIMENTACAO ADAPTATIVA
# ==========================================

def andar_interno(
    distancia,
    angulo=0,
    inicio=45,
    velocidade=60,
    final=30,
    subida=300,
    descida=250
):

    global memoria_frente
    global memoria_re

    parar()

    if not esperar_imu():
        return False

    hub.imu.reset_heading(0)

    mL.reset_angle(0)
    mR.reset_angle(0)

    sentido = 1 if distancia >= 0 else -1
    total = abs(distancia)

    if total == 0:
        return True

    memoria = (
        memoria_frente if sentido > 0 else memoria_re
    )

    ultimo_erro = 0
    derivada_suave = 0
    correcao_suave = 0

    relogio = StopWatch()
    ultimo_tempo = relogio.time()

    ultimo_angulo_l = mL.angle()
    ultimo_angulo_r = mR.angle()

    ultimo_mov_l = 0
    ultimo_mov_r = 0

    tempo_limite = max(8000, 5000 + total * 15)

    while (
        distancia_percorrida() < total
        and relogio.time() < tempo_limite
    ):

        if not verificar_competicao():
            parar()
            return False

        agora = relogio.time()
        atual = distancia_percorrida()

        vel = velocidade_rampa(
            atual,
            total,
            inicio,
            velocidade,
            final,
            subida,
            descida
        )

        vel *= sentido

        angulo_l = mL.angle()
        angulo_r = mR.angle()

        if abs(angulo_l - ultimo_angulo_l) >= 1:
            ultimo_angulo_l = angulo_l
            ultimo_mov_l = agora

        if abs(angulo_r - ultimo_angulo_r) >= 1:
            ultimo_angulo_r = angulo_r
            ultimo_mov_r = agora

        if agora - ultimo_mov_l > 1500:
            parar()
            print("VERIFICAR MOTOR E")
            registrar_falha()
            return False

        if agora - ultimo_mov_r > 1500:
            parar()
            print("VERIFICAR MOTOR F")
            registrar_falha()
            return False

        erro = angulo - hub.imu.heading()

        dt = (agora - ultimo_tempo) / 1000
        dt = limitar(dt, 0.005, 0.05)

        ultimo_tempo = agora

        derivada = (erro - ultimo_erro) / dt

        derivada_suave = (
            0.75 * derivada_suave
            + 0.25 * derivada
        )

        if (
            abs(erro) < 8
            and abs(derivada_suave) < 40
        ):

            memoria += erro * KI_G * dt

            memoria = limitar(
                memoria,
                -MAX_MEMORIA,
                MAX_MEMORIA
            )

        correcao = (
            KP_G * erro
            + memoria
            + KD_G * derivada_suave
        )

        correcao = limitar(
            correcao,
            -MAX_CORRECAO,
            MAX_CORRECAO
        )

        correcao_suave = (
            0.65 * correcao_suave
            + 0.35 * correcao
        )

        mL.dc(limitar(vel + correcao_suave))
        mR.dc(limitar(vel - correcao_suave))

        ultimo_erro = erro

        wait(10)

    parar()

    if not verificar_competicao():
        return False

    if distancia_percorrida() < total:
        print("TEMPO LIMITE ATINGIDO")
        registrar_falha()
        return False

    if sentido > 0:
        memoria_frente = memoria
    else:
        memoria_re = memoria

    print("MOVIMENTO CONCLUIDO")
    print("MEMORIA ATUAL:", memoria)

    registrar_sucesso()
    return True


# ==========================================
# COMANDOS PERSONALIZAVEIS
# ==========================================

def andar(distancia_mm, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_ANDAR

    velocidade = limitar(
        velocidade,
        VELOCIDADE_MINIMA,
        VELOCIDADE_MAXIMA
    )

    graus_motor = (
        distancia_mm * 360
        / (3.14159265 * DIAMETRO_RODA)
    )

    return andar_interno(
        graus_motor,
        inicio=VELOCIDADE_INICIAL,
        velocidade=velocidade,
        final=VELOCIDADE_FINAL,
        subida=300,
        descida=250
    )


def girar(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GIRAR

    velocidade = limitar(
        velocidade,
        VELOCIDADE_MINIMA,
        VELOCIDADE_MAXIMA
    )

    return giro_interno(
        angulo,
        velocidade=velocidade
    )


def girar_roda(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GIRAR

    velocidade = limitar(
        velocidade,
        VELOCIDADE_MINIMA,
        VELOCIDADE_MAXIMA
    )

    return giro_uma_roda_interno(
        angulo,
        velocidade=velocidade
    )


def esperar(tempo):
    return esperar_controlado(tempo)


def parar_missao():
    solicitar_parada()
    parar()
    parar_garras()
    return True


# ==========================================
# CONSULTAR APRENDIZADO
# ==========================================

def mostrar_aprendizado():

    print("======================")
    print("RABBITECH AUTOPILOT V3.2")
    print("======================")

    print("MEMORIA FRENTE:", memoria_frente)
    print("MEMORIA RE:", memoria_re)

    print("MOVIMENTOS OK:", movimentos_concluidos)
    print("MOVIMENTOS COM ERRO:", movimentos_falhos)

    print("======================")