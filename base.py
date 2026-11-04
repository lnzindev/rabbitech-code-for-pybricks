
# ==========================================
# RABBITECH - AUTOPILOT V4.0
# Pybricks MicroPython 3.6.1
#
# C = GARRA ESQUERDA
# D = GARRA DIREITA
# E = TRACAO ESQUERDA
# F = TRACAO DIREITA
#
# RODAS: 56 MM
# ACELERACAO E FRENAGEM SUAVES
# GIROS COM DESACELERACAO
# CORRECAO DE DIRECAO
# MEMORIA ADAPTATIVA
# PROTECAO CONTRA TRAVAMENTO
# ==========================================

from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import Motor
from pybricks.tools import wait, StopWatch

# ==========================================
# INICIALIZACAO
# ==========================================

hub = PrimeHub()

mL = Motor(Port.E, Direction.COUNTERCLOCKWISE)
mR = Motor(Port.F, Direction.CLOCKWISE)

garra_esq = Motor(Port.C)
garra_dir = Motor(Port.D)

DIAMETRO_RODA = 56
PI = 3.14159265

# ==========================================
# CONFIGURACOES PERSONALIZAVEIS
# ==========================================

VELOCIDADE_ANDAR = 60
VELOCIDADE_GIRAR = 45
VELOCIDADE_GARRA = 300

VELOCIDADE_MINIMA = 10
VELOCIDADE_MAXIMA = 100

# RAMPA DE MOVIMENTO
VELOCIDADE_INICIAL = 10
VELOCIDADE_FINAL = 0

DISTANCIA_ACELERACAO = 150
DISTANCIA_DESACELERACAO = 180

# RAMPA DOS GIROS
GIRO_VELOCIDADE_MINIMA = 7
GIRO_INICIO_DESACELERACAO = 25

# GARRAS
ANGULO_GARRA_ABERTA = 90
ANGULO_GARRA_FECHADA = 90

# PROTECAO
TEMPO_SEM_MOVIMENTO = 1500
TEMPO_EXTRA_MOVIMENTO = 8000

# ==========================================
# CORRECAO DE DIRECAO
# ==========================================

KP_G = 1.4
KI_G = 0.12
KD_G = 0.006

MAX_CORRECAO = 16
MAX_MEMORIA = 7

memoria_frente = 0.0
memoria_re = 0.0

# ==========================================
# CONTROLE DOS GIROS
# ==========================================

KP_T = 1.5

TOLERANCIA_GIRO = 1.5
TIMEOUT_GIRO = 10000

COMPENSACAO_DIREITA = 3

# ==========================================
# CONTADORES
# ==========================================

movimentos_concluidos = 0
movimentos_falhos = 0

# ==========================================
# MEMORIA PERMANENTE
# ==========================================

ASSINATURA = b"RBT4"
TAMANHO_MEMORIA = 12


def codificar_16(valor):

    valor = int(valor)
    valor = max(0, min(65535, valor))

    return bytes([
        valor // 256,
        valor % 256
    ])


def decodificar_16(dados, posicao):

    return (
        dados[posicao] * 256
        + dados[posicao + 1]
    )


def codificar_memoria(valor):

    numero = int(valor * 1000)
    numero = max(-7000, min(7000, numero))

    return codificar_16(numero + 32768)


def decodificar_memoria(dados, posicao):

    numero = decodificar_16(dados, posicao) - 32768

    return numero / 1000


def salvar_aprendizado():

    dados = ASSINATURA
    dados += codificar_memoria(memoria_frente)
    dados += codificar_memoria(memoria_re)
    dados += codificar_16(movimentos_concluidos)
    dados += codificar_16(movimentos_falhos)

    try:

        hub.system.storage(0, write=dados)

        print("APRENDIZADO SALVO")
        return True

    except Exception as erro:

        print("ERRO AO SALVAR:", erro)
        return False


def carregar_aprendizado():

    global memoria_frente
    global memoria_re
    global movimentos_concluidos
    global movimentos_falhos

    try:

        dados = hub.system.storage(
            0,
            read=TAMANHO_MEMORIA
        )

        if len(dados) != TAMANHO_MEMORIA:

            print("MEMORIA NOVA")
            return False

        if dados[0:4] != ASSINATURA:

            print("INICIANDO APRENDIZADO")
            return False

        memoria_frente = decodificar_memoria(dados, 4)
        memoria_re = decodificar_memoria(dados, 6)

        movimentos_concluidos = decodificar_16(dados, 8)
        movimentos_falhos = decodificar_16(dados, 10)

        print("MEMORIA RECUPERADA")
        return True

    except Exception as erro:

        print("ERRO AO LER MEMORIA:", erro)
        return False


def registrar_falha():

    global movimentos_falhos

    movimentos_falhos = min(
        65535,
        movimentos_falhos + 1
    )

    print("MOVIMENTO FALHOU")
    salvar_aprendizado()


def registrar_sucesso():

    global movimentos_concluidos

    movimentos_concluidos = min(
        65535,
        movimentos_concluidos + 1
    )

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
        wait(10)


def parar():

    mL.hold()
    mR.hold()
    wait(100)


def parar_garras():

    garra_esq.hold()
    garra_dir.hold()


def distancia_percorrida():

    return (
        abs(mL.angle()) + abs(mR.angle())
    ) / 2


def normalizar_erro(erro):

    return (erro + 180) % 360 - 180


# ==========================================
# RAMPA SUAVE
# ==========================================

def suavizar(progresso):

    progresso = limitar(progresso, 0, 1)

    return (
        progresso
        * progresso
        * (3 - 2 * progresso)
    )


def velocidade_rampa(
    atual,
    total,
    inicio,
    alvo,
    final,
    subida,
    descida
):

    if subida <= 0:
        velocidade_subida = alvo

    else:

        progresso = suavizar(
            atual / subida
        )

        velocidade_subida = (
            inicio
            + (alvo - inicio) * progresso
        )

    if descida <= 0:
        velocidade_descida = alvo

    else:

        restante = max(0, total - atual)

        progresso = suavizar(
            restante / descida
        )

        velocidade_descida = (
            final
            + (alvo - final) * progresso
        )

    # Escolhe o perfil mais lento.
    # Isso permite rampas que se sobrepoem
    # em trajetos curtos.

    velocidade = min(
        velocidade_subida,
        velocidade_descida
    )

    return limitar(velocidade, 0, 100)


# ==========================================
# CONTROLE DAS GARRAS
# ==========================================

def garra_esquerda(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    garra_esq.run_angle(velocidade, angulo)

    return True


def garra_direita(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    garra_dir.run_angle(velocidade, angulo)

    return True


def abrir_garras():

    garra_esquerda(-ANGULO_GARRA_ABERTA)
    garra_direita(ANGULO_GARRA_ABERTA)

    return True


def fechar_garras():

    garra_esquerda(ANGULO_GARRA_FECHADA)
    garra_direita(-ANGULO_GARRA_FECHADA)

    return True


# ==========================================
# GIRO CONTINUO DO IMU
# Permite acompanhar giros acima de 180 graus
# ==========================================

def atualizar_giro_continuo(anterior, acumulado):

    atual = hub.imu.heading()

    diferenca = atual - anterior
    diferenca = normalizar_erro(diferenca)

    acumulado += diferenca

    return atual, acumulado


# ==========================================
# CONTROLE DE VELOCIDADE DOS GIROS
# ==========================================

def calcular_giro(erro, velocidade):

    intensidade = abs(erro) * KP_T

    correcao = min(
        velocidade,
        intensidade
    )

    correcao = max(
        GIRO_VELOCIDADE_MINIMA,
        correcao
    )

    return limitar(
        correcao,
        GIRO_VELOCIDADE_MINIMA,
        velocidade
    )


# ==========================================
# GIRO COM DUAS RODAS
# ==========================================

def giro_interno(angulo, velocidade=45):

    parar()
    esperar_imu()

    hub.imu.reset_heading(0)

    anterior = hub.imu.heading()
    acumulado = 0

    relogio = StopWatch()
    concluiu = False

    while relogio.time() < TIMEOUT_GIRO:

        anterior, acumulado = atualizar_giro_continuo(
            anterior,
            acumulado
        )

        erro = angulo - acumulado

        if abs(erro) <= TOLERANCIA_GIRO:

            concluiu = True
            break

        correcao = calcular_giro(
            erro,
            velocidade
        )

        if erro > 0:

            mL.dc(correcao)
            mR.dc(-correcao)

        else:

            mL.dc(-correcao)
            mR.dc(correcao)

        wait(5)

    parar()

    if not concluiu:

        print("ERRO NO GIRO")
        registrar_falha()

        return False

    registrar_sucesso()

    return True


# ==========================================
# GIRO COM UMA RODA
# ==========================================

def giro_uma_roda_interno(angulo, velocidade=45):

    parar()
    esperar_imu()

    hub.imu.reset_heading(0)

    anterior = hub.imu.heading()
    acumulado = 0

    relogio = StopWatch()
    concluiu = False

    if angulo > 0:
        mR.hold()
    else:
        mL.hold()

    while relogio.time() < TIMEOUT_GIRO:

        anterior, acumulado = atualizar_giro_continuo(
            anterior,
            acumulado
        )

        erro = angulo - acumulado

        if abs(erro) <= TOLERANCIA_GIRO:

            concluiu = True
            break

        correcao = calcular_giro(
            erro,
            velocidade
        )

        if angulo > 0:
            mL.dc(correcao)

        else:
            mR.dc(-correcao)

        wait(5)

    parar()

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
    inicio=10,
    velocidade=60,
    final=0,
    subida=300,
    descida=350
):

    global memoria_frente
    global memoria_re

    parar()
    esperar_imu()

    hub.imu.reset_heading(0)

    mL.reset_angle(0)
    mR.reset_angle(0)

    sentido = 1 if distancia >= 0 else -1
    total = abs(distancia)

    if total == 0:
        return True

    memoria = (
        memoria_frente
        if sentido > 0
        else memoria_re
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

    tempo_limite = (
        TEMPO_EXTRA_MOVIMENTO
        + total * 20
    )

    while (
        distancia_percorrida() < total
        and relogio.time() < tempo_limite
    ):

        agora = relogio.time()

        atual = distancia_percorrida()

        # RAMPA DE ACELERACAO E FRENAGEM

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

        # MONITORAMENTO DOS MOTORES

        angulo_l = mL.angle()
        angulo_r = mR.angle()

        if abs(angulo_l - ultimo_angulo_l) >= 1:

            ultimo_angulo_l = angulo_l
            ultimo_mov_l = agora

        if abs(angulo_r - ultimo_angulo_r) >= 1:

            ultimo_angulo_r = angulo_r
            ultimo_mov_r = agora

        if agora - ultimo_mov_l > TEMPO_SEM_MOVIMENTO:

            parar()

            print("VERIFICAR MOTOR E")

            registrar_falha()

            return False

        if agora - ultimo_mov_r > TEMPO_SEM_MOVIMENTO:

            parar()

            print("VERIFICAR MOTOR F")

            registrar_falha()

            return False

        # CORRECAO DE DIRECAO

        erro = normalizar_erro(
            angulo - hub.imu.heading()
        )

        dt = (agora - ultimo_tempo) / 1000

        dt = limitar(dt, 0.005, 0.05)

        ultimo_tempo = agora

        derivada = (
            erro - ultimo_erro
        ) / dt

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

        # COMANDO DOS MOTORES

        velocidade_esq = limitar(
            vel + correcao_suave
        )

        velocidade_dir = limitar(
            vel - correcao_suave
        )

        mL.dc(velocidade_esq)
        mR.dc(velocidade_dir)

        ultimo_erro = erro

        wait(10)

    parar()

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
        / (PI * DIAMETRO_RODA)
    )

    subida_graus = (
        DISTANCIA_ACELERACAO * 360
        / (PI * DIAMETRO_RODA)
    )

    descida_graus = (
        DISTANCIA_DESACELERACAO * 360
        / (PI * DIAMETRO_RODA)
    )

    return andar_interno(
        graus_motor,
        inicio=VELOCIDADE_INICIAL,
        velocidade=velocidade,
        final=VELOCIDADE_FINAL,
        subida=subida_graus,
        descida=descida_graus
    )


def girar(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GIRAR

    velocidade = limitar(
        velocidade,
        VELOCIDADE_MINIMA,
        VELOCIDADE_MAXIMA
    )

    if angulo < 0:
        angulo -= COMPENSACAO_DIREITA

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

    wait(tempo)

    return True


# ==========================================
# CALIBRACAO
# ==========================================

def ajustar_roda(diametro):

    global DIAMETRO_RODA

    if diametro <= 0:
        print("DIAMETRO INVALIDO")
        return False

    DIAMETRO_RODA = diametro

    print("DIAMETRO AJUSTADO:", DIAMETRO_RODA)

    return True


def ajustar_rampa(aceleracao, desaceleracao):

    global DISTANCIA_ACELERACAO
    global DISTANCIA_DESACELERACAO

    DISTANCIA_ACELERACAO = max(0, aceleracao)

    DISTANCIA_DESACELERACAO = max(0, desaceleracao)

    print("RAMPA ATUALIZADA")

    return True


# ==========================================
# CONSULTAR APRENDIZADO
# ==========================================

def mostrar_aprendizado():

    print("======================")
    print("RABBITECH AUTOPILOT V4.0")
    print("======================")

    print("MEMORIA FRENTE:", memoria_frente)
    print("MEMORIA RE:", memoria_re)

    print("MOVIMENTOS OK:", movimentos_concluidos)
    print("MOVIMENTOS COM ERRO:", movimentos_falhos)

    print("DIAMETRO RODA:", DIAMETRO_RODA)

    print("ACELERACAO:", DISTANCIA_ACELERACAO)
    print("DESACELERACAO:", DISTANCIA_DESACELERACAO)

    print("======================")
