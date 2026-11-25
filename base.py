
from math import pi, sqrt

from pybricks.hubs import PrimeHub
from pybricks.parameters import Button, Direction, Port, Stop
from pybricks.pupdevices import Motor
from pybricks.tools import StopWatch, wait
import memoria as memoria_store


# ==========================================
# CONFIGURACOES DO ROBO
# ==========================================

DIAMETRO_RODA = 56

VELOCIDADE_ANDAR = 60
VELOCIDADE_GIRAR = 78
VELOCIDADE_GARRA = 300

ANGULO_GARRA_ABERTA = 90
ANGULO_GARRA_FECHADA = 90

TOLERANCIA_GIRO = 1.5
LIMITE_APROXIMACAO = 5000
LIMITE_GIRO = 8000

TEMPO_COMPETICAO = 150000
SINAL_GIRO = 1


# ==========================================
# PID DE DIRECAO AJUSTADO
# ==========================================

KP = 1.20
KD = 0.025
KI = 0.0

LIMITE_MEMORIA = 0
LIMITE_CORRECAO = 10

FILTRO_DERIVADA = 0.80
FILTRO_CORRECAO = 0.75


# ==========================================
# VELOCIDADE E ACELERACAO
# ==========================================

FATOR_VELOCIDADE_UTIL = 0.78

ACELERACAO_ANDAR = 1800
ACELERACAO_FREIO = 2200


# ==========================================
# INICIALIZACAO
# ==========================================

hub = PrimeHub()


def conectar_motor(porta, nome, sentido=Direction.CLOCKWISE):
    try:
        return Motor(porta, sentido)
    except OSError:
        print("VERIFIQUE O MOTOR:", porta, nome)
        raise


mL = conectar_motor(
    Port.E,
    "TRACAO ESQUERDA",
    Direction.COUNTERCLOCKWISE
)

mR = conectar_motor(
    Port.F,
    "TRACAO DIREITA"
)

garra_esq = conectar_motor(
    Port.C,
    "GARRA ESQUERDA"
)

garra_dir = conectar_motor(
    Port.D,
    "GARRA DIREITA"
)

hub.system.set_stop_button(None)


memoria_frente, memoria_re, movimentos_concluidos, movimentos_falhos = (
    memoria_store.carregar(hub)
)

_relogio_rodada = None
_parada = False


# ==========================================
# LIMITADORES
# ==========================================

def limitar(valor, minimo=-100, maximo=100):
    return max(minimo, min(maximo, valor))


def limite_velocidade_motores():
    try:
        limite_esquerdo = abs(int(mL.control.limits()[0]))
        limite_direito = abs(int(mR.control.limits()[0]))

        limite = min(limite_esquerdo, limite_direito)

        if limite > 0:
            return limite

    except Exception as erro:
        print("NAO FOI POSSIVEL LER LIMITE DOS MOTORES:", erro)

    return 1000


# ==========================================
# COMPETICAO
# ==========================================

def iniciar_competicao():
    global _relogio_rodada, _parada

    hub.system.set_stop_button(None)

    _relogio_rodada = StopWatch()
    _parada = False

    return True


def solicitar_parada():
    global _parada

    _parada = True

    return True


def verificar_competicao():
    global _parada

    if not _parada and Button.CENTER in hub.buttons.pressed():
        print("PARADA PELO BOTAO CENTRAL")
        _parada = True

    if not _parada and _relogio_rodada is not None:
        if _relogio_rodada.time() >= TEMPO_COMPETICAO:
            print("TEMPO DA RODADA ESGOTADO")
            _parada = True

    return not _parada


def esperar(tempo):
    relogio = StopWatch()

    while relogio.time() < tempo:
        if not verificar_competicao():
            return False

        wait(min(10, max(1, int(tempo - relogio.time()))))

    return verificar_competicao()


def esperar_imu():
    while not hub.imu.ready():
        if not esperar(10):
            return False

    return verificar_competicao()


# ==========================================
# PARADA DOS MOTORES
# ==========================================

def parar():
    try:
        mL.hold()
    finally:
        mR.hold()


def parar_garras():
    try:
        garra_esq.hold()
    finally:
        garra_dir.hold()

    return True


def parar_todos():
    ok = True

    for porta, motor in (
        (Port.E, mL),
        (Port.F, mR),
        (Port.C, garra_esq),
        (Port.D, garra_dir)
    ):
        try:
            motor.hold()
        except OSError as erro:
            print("ERRO AO PARAR MOTOR:", porta, erro)
            ok = False

    return ok


def parar_missao():
    solicitar_parada()
    return parar_todos()


def finalizar_competicao():
    global _relogio_rodada

    _relogio_rodada = None

    try:
        return parar_todos()
    finally:
        hub.system.set_stop_button(Button.CENTER)


# ==========================================
# REGISTRO DE MOVIMENTOS
# ==========================================

def registrar_movimento(ok):
    global movimentos_concluidos, movimentos_falhos

    if ok:
        movimentos_concluidos = min(
            65535,
            movimentos_concluidos + 1
        )
    else:
        movimentos_falhos = min(
            65535,
            movimentos_falhos + 1
        )

    memoria_store.salvar(
        hub,
        memoria_frente,
        memoria_re,
        movimentos_concluidos,
        movimentos_falhos
    )

    return ok


# ==========================================
# GARRAS
# ==========================================

def mover_motor(motor, angulo, velocidade):
    if not verificar_competicao():
        return False

    porta = "C (esquerda)" if motor is garra_esq else "D (direita)"

    velocidade = max(1, abs(velocidade))

    inicio = motor.angle()

    tolerancia = min(4, abs(angulo) * 0.10)

    prazo = 2500 + int(abs(angulo) / velocidade * 2000)

    relogio = StopWatch()

    melhor_erro = abs(angulo)
    ultimo_avanco = 0
    dentro_desde = None

    print("GARRA", porta, "ALVO:", angulo)

    try:
        motor.run_angle(
            velocidade,
            angulo,
            then=Stop.HOLD,
            wait=False
        )

        while verificar_competicao():
            agora = relogio.time()

            real = motor.angle() - inicio
            erro = abs(angulo - real)

            if erro <= tolerancia:
                if dentro_desde is None:
                    dentro_desde = agora

                if motor.done() or agora - dentro_desde >= 100:
                    print("GARRA", porta, "CONCLUIDA. REAL:", real)
                    return True
            else:
                dentro_desde = None

            if melhor_erro - erro >= 1:
                melhor_erro = erro
                ultimo_avanco = agora

            if agora - ultimo_avanco >= 1500 or agora >= prazo:
                print("GARRA", porta, "ALVO:", angulo, "REAL:", real)
                print("GARRA FORA DO ALVO. VERIFIQUE O CURSO E O SENTIDO.")
                return False

            wait(10)

        return False

    finally:
        motor.hold()


def garra_esquerda(angulo, velocidade=None):
    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor(garra_esq, angulo, velocidade)


def garra_direita(angulo, velocidade=None):
    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor(garra_dir, angulo, velocidade)


def abrir_garras():
    return garra_esquerda(-ANGULO_GARRA_ABERTA) and garra_direita(
        ANGULO_GARRA_ABERTA
    )


def fechar_garras():
    return garra_esquerda(ANGULO_GARRA_FECHADA) and garra_direita(
        -ANGULO_GARRA_FECHADA
    )


# ==========================================
# ANDAR COM PID AJUSTADO + IMU
# ==========================================

def andar(distancia_mm, velocidade=None):
    global memoria_frente, memoria_re

    if velocidade is None:
        velocidade = VELOCIDADE_ANDAR

    percentual = limitar(abs(velocidade), 10, 100)

    limite_motor = limite_velocidade_motores()

    velocidade_base = (
        limite_motor *
        FATOR_VELOCIDADE_UTIL *
        percentual / 100
    )

    alvo = abs(distancia_mm) * 360 / (pi * DIAMETRO_RODA)

    sentido = 1 if distancia_mm >= 0 else -1

    # Zera a memoria antiga para evitar puxar para um lado.
    memoria = 0.0

    parar()

    if not esperar_imu():
        return False

    if alvo == 0:
        return True

    hub.imu.reset_heading(0)

    inicio_l = mL.angle()
    inicio_r = mR.angle()

    ultimo_l = inicio_l
    ultimo_r = inicio_r

    tempo_l = 0
    tempo_r = 0
    tempo_anterior = 0

    erro_anterior = 0
    derivada = 0
    correcao = 0

    velocidade_atual = 0

    relogio = StopWatch()

    prazo = max(8000, 5000 + alvo * 15)

    ok = False

    try:
        while verificar_competicao():
            agora = relogio.time()

            l = mL.angle()
            r = mR.angle()

            progresso_l = (l - inicio_l) * sentido
            progresso_r = (r - inicio_r) * sentido

            progresso = (progresso_l + progresso_r) / 2

            restante = alvo - progresso

            if restante <= 0:
                ok = True
                break

            if agora >= prazo:
                print("TEMPO LIMITE AO ANDAR:", distancia_mm)
                break

            if abs(l - ultimo_l) >= 1:
                ultimo_l = l
                tempo_l = agora

            if abs(r - ultimo_r) >= 1:
                ultimo_r = r
                tempo_r = agora

            if agora - tempo_l > 1500 or agora - tempo_r > 1500:
                porta = Port.E if agora - tempo_l > 1500 else Port.F

                print("MOTOR SEM MOVIMENTO:", porta)
                print("VELOCIDADE REAL E/F:", mL.speed(), mR.speed())
                print("CARGA E/F:", mL.load(), mR.load())

                break

            # PERFIL DE ACELERACAO E FRENAGEM

            dt = limitar(
                (agora - tempo_anterior) / 1000,
                0.005,
                0.05
            )

            velocidade_frenagem = sqrt(
                max(0, 2 * ACELERACAO_FREIO * restante)
            )

            velocidade_desejada = min(
                velocidade_base,
                velocidade_frenagem
            )

            if velocidade_atual < velocidade_desejada:
                velocidade_atual = min(
                    velocidade_desejada,
                    velocidade_atual + ACELERACAO_ANDAR * dt
                )
            else:
                velocidade_atual = max(
                    velocidade_desejada,
                    velocidade_atual - ACELERACAO_FREIO * dt
                )

            # PID DE DIRECAO

            erro = -hub.imu.heading()

            derivada_bruta = (erro - erro_anterior) / dt

            derivada = (
                FILTRO_DERIVADA * derivada +
                (1 - FILTRO_DERIVADA) * derivada_bruta
            )

            ajuste = (
                KP * erro +
                memoria +
                KD * derivada
            )

            ajuste = limitar(
                ajuste,
                -LIMITE_CORRECAO,
                LIMITE_CORRECAO
            )

            correcao = (
                FILTRO_CORRECAO * correcao +
                (1 - FILTRO_CORRECAO) * ajuste
            )

            correcao_velocidade = (
                velocidade_atual * correcao / 100
            )

            velocidade_esquerda = (
                velocidade_atual + correcao_velocidade
            ) * sentido

            velocidade_direita = (
                velocidade_atual - correcao_velocidade
            ) * sentido

            mL.run(int(velocidade_esquerda))
            mR.run(int(velocidade_direita))

            tempo_anterior = agora
            erro_anterior = erro

            wait(10)

    finally:
        parar()

    if not verificar_competicao():
        return False

    if ok:
        if sentido > 0:
            memoria_frente = memoria
        else:
            memoria_re = memoria

    return registrar_movimento(ok)


# ==========================================
# GIROS PELA IMU
# MANTIDOS DA VERSAO ANTERIOR
# ==========================================

def _girar(alvo, velocidade, uma_roda):
    if velocidade is None:
        velocidade = VELOCIDADE_GIRAR

    limite = limitar(abs(velocidade), 30, 55)

    mover_l = not uma_roda or alvo > 0
    mover_r = not uma_roda or alvo < 0

    parar()

    if not esperar_imu() or not esperar(200):
        return False

    hub.imu.reset_heading(0)

    relogio = StopWatch()

    razao = 2.9 if uma_roda else 1.45

    minimo_passo = 3
    lado_anterior = 0

    try:
        anterior = hub.imu.heading()
        tempo_anterior = relogio.time()

        while relogio.time() < LIMITE_APROXIMACAO:
            if not verificar_competicao():
                return False

            atual = hub.imu.heading()
            agora = relogio.time()

            erro = alvo - atual
            restante = abs(erro)

            if restante <= 6 or alvo * erro < 0:
                break

            lado = 1 if erro > 0 else -1

            taxa = (
                (atual - anterior) * 1000 /
                max(1, agora - tempo_anterior)
            )

            if restante > 35:
                potencia = limite
            elif restante > 15:
                potencia = max(30, limite * 0.75)
            else:
                potencia = max(30, limite * 0.60)

            if taxa * lado > 180 and restante < 45:
                potencia = -30
            elif taxa * lado > 100 and restante < 35:
                potencia = 7

            comando = int(limitar(
                lado * potencia * SINAL_GIRO,
                -limite,
                limite
            ))

            if mover_l:
                mL.dc(comando)

            if mover_r:
                mR.dc(-comando)

            anterior = atual
            tempo_anterior = agora

            wait(10)

        parar()

        if not esperar(150):
            return False

        while relogio.time() < LIMITE_GIRO and verificar_competicao():
            antes = hub.imu.heading()

            erro = alvo - antes

            if abs(erro) <= TOLERANCIA_GIRO:
                break

            lado = 1 if erro > 0 else -1

            if lado_anterior and lado != lado_anterior:
                minimo_passo = 3

            lado_anterior = lado

            graus = int(limitar(
                razao * abs(erro) * 0.85,
                minimo_passo,
                42
            ))

            comando = lado * graus * SINAL_GIRO

            velocidade_passo = int(limitar(
                70 + graus * 3,
                85,
                200
            ))

            l0 = mL.angle()
            r0 = mR.angle()

            direcao = "DIREITA" if erro > 0 else "ESQUERDA"

            print("CORRIGINDO", direcao, "ERRO:", erro)

            if mover_l:
                mL.run_angle(
                    velocidade_passo,
                    comando,
                    then=Stop.HOLD,
                    wait=False
                )

            if mover_r:
                mR.run_angle(
                    velocidade_passo,
                    -comando,
                    then=Stop.HOLD,
                    wait=False
                )

            prazo_correcao = min(
                LIMITE_GIRO,
                relogio.time() + 700
            )

            while relogio.time() < prazo_correcao:
                if not verificar_competicao():
                    return False

                if (not mover_l or mL.done()) and (
                    not mover_r or mR.done()
                ):
                    break

                wait(10)

            else:
                print("MOTOR NAO TERMINOU A CORRECAO")
                break

            if not esperar(150):
                return False

            progresso = (
                (hub.imu.heading() - antes) * lado
            )

            rodas = (
                (abs(mL.angle() - l0) +
                 abs(mR.angle() - r0)) /
                (1 if uma_roda else 2)
            )

            if progresso >= 0.25 and rodas >= graus * 0.5:
                medida = rodas / progresso

                razao = limitar(
                    medida,
                    max(0.8, razao * 0.65),
                    min(24, razao * 2)
                )

                minimo_passo = 3
            else:
                minimo_passo = min(
                    18,
                    minimo_passo + 3
                )

    finally:
        parar()

    if not verificar_competicao():
        return False

    real = hub.imu.heading()
    erro = alvo - real

    print(
        "GIRO ALVO:", alvo,
        "GIRO REAL:", real,
        "ERRO FINAL:", erro
    )

    if abs(erro) <= TOLERANCIA_GIRO:
        return registrar_movimento(True)

    print("GIRO FORA DA TOLERANCIA")

    return registrar_movimento(False)


def girar(angulo, velocidade=None):
    return _girar(angulo, velocidade, False)


def girar_roda(angulo, velocidade=None):
    return _girar(angulo, velocidade, True)


# ==========================================
# APRENDIZADO
# ==========================================

def mostrar_aprendizado():
    print("RABBITECH AUTOPILOT V3.5")

    print("MEMORIA FRENTE:", memoria_frente)
    print("MEMORIA RE:", memoria_re)

    print("MOVIMENTOS OK:", movimentos_concluidos)
    print("MOVIMENTOS COM ERRO:", movimentos_falhos)
