
# ==========================================
# RABBITECH - AUTOPILOT V3.3
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

# O botao central sera monitorado pelo proprio programa.
# Sem isso, o firmware encerra o script imediatamente ao pressionar CENTER.
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
VELOCIDADE_GIRAR = 78
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

TEMPO_COMPETICAO = 150000  # 2 minutos e 30 segundos
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

    # CENTER e reconhecido antes, durante e depois da rodada.
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

KP_T = 1.8
KD_T = 0.35

TOLERANCIA_GIRO = 1.5
TIMEOUT_GIRO = 8000

# Controle do giro pela IMU.
# O heading positivo do Pybricks corresponde a giro horario.
# O giro usa somente a IMU durante a manobra.
# Nao existe pulso de calibracao antes do giro: ele deslocava o robo
# aproximadamente 80 graus e depois zerava a leitura, escondendo o movimento.
# Calibracao baseada nos testes fisicos do robo na mesa.
# Abaixo de 20% os motores quase nao vencem o atrito inicial.
POTENCIA_MIN_GIRO = 30
POTENCIA_MAX_GIRO = 55
SINAL_GIRO = 1

# Refinamento final do giro.
# Causa do erro antigo: pulsos de 22-33% por 15-85 ms nao vencem o atrito
# estatico do pivo, entao o robo nao saia do lugar (o erro ficava identico
# nas 5 tentativas). Agora a fase final usa o controle de posicao dos
# motores (run_angle), que aumenta o torque ate o motor realmente andar,
# e a IMU confere o resultado de cada tentativa.
FIM_FASE_DC = 6.0                # graus: abaixo disso o giro por potencia termina

# O refino so continua enquanto o erro for MAIOR que a tolerancia de aceite.
# Tentar chegar a 1.0 deg quando 1.5 deg ja e aceito nao muda aprovado/reprovado,
# gasta ~0.3-0.5 s por giro e, como a menor correcao de roda (3 graus de
# roda ~ 2 graus de giro) e maior que a faixa 1.0-1.5, pode ultrapassar o alvo.
TOLERANCIA_ALVO_REFINO = TOLERANCIA_GIRO

LIMITE_ERRO_CORRECAO = 25.0      # graus: erro maior que isso nao e refino
MAX_TENTATIVAS_CORRECAO = 3
TEMPO_MAX_CORRECAO =   1000        # ms: orcamento TOTAL do refino (movimentos + esperas)
MOV_TIMEOUT_MAX = 1000           # ms: teto de um unico movimento de refino
MARGEM_MOVIMENTO_MS = 100        # ms somados a estimativa de duracao do movimento
ESPERA_ASSENTAR_GIRO = 150       # ms para o robo parar antes de ler a IMU
MIN_GRAUS_RODA_REFINO = 3        # menor movimento de roda que vale comandar
VEL_REFINO_MIN = 80              # graus/s do motor
VEL_REFINO_MAX = 200

# Razao roda/giro (graus de roda por grau de giro do robo).
# Limites: 0.8 ~ distancia entre rodas de 45 mm; 4.0 ~ 225 mm.
RAZAO_RODA_PADRAO = 1.45         # valor inicial/fallback
RAZAO_RODA_MIN = 0.8
RAZAO_RODA_MAX = 4.0
MIN_DESLOC_CALIBRACAO = 20.0     # graus: giro minimo para aprender a razao
RAZAO_DESVIO_MAX = 0.5           # medida >50% longe da aprendida e "suspeita"
RAZAO_ASSIMETRIA_MAX = 0.3       # diferenca maxima entre as duas rodas (fracao)
MIN_PROGRESSO_RAZAO = 0.5        # graus: menor avanco da IMU que serve de medida
_razao_aprendida = RAZAO_RODA_PADRAO
_razao_suspeita = None

# Estado do ultimo movimento supervisionado das rodas (para log e decisao).
_status_mov = "NENHUM"           # CONCLUIDO / TIMEOUT / INTERROMPIDO
_duracao_mov = 0

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

    (memoria_frente, memoria_re,
     movimentos_concluidos, movimentos_falhos) = memoria_store.carregar(hub)
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

    # Parar os motores nao significa encerrar a rodada.
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
    # wait=False permite verificar CENTER e o limite de 150 s
    # enquanto a garra esta em movimento.
    if not verificar_competicao():
        return False

    motor.run_angle(velocidade, angulo, then=Stop.HOLD, wait=False)

    while not motor.done():
        if not verificar_competicao():
            motor.hold()
            return False
        wait(10)

    return verificar_competicao()


def garra_esquerda(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor_supervisionado(garra_esq, angulo, velocidade)


def garra_direita(angulo, velocidade=None):

    if velocidade is None:
        velocidade = VELOCIDADE_GARRA

    return mover_motor_supervisionado(garra_dir, angulo, velocidade)


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

    minimo = min(9, velocidade) if abs(erro) > 10 else min(4, velocidade)

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

def mover_rodas_supervisionado(graus_l, graus_r, velocidade, timeout=MOV_TIMEOUT_MAX):
    """
    Move as duas rodas por posicao (Stop.HOLD) ate AMBAS terminarem.

    Retorna True SOMENTE se os dois motores concluiram o movimento.
    Em timeout ou interrupcao (CENTER / 150 s) os dois motores sao
    parados na hora e retorna False. O motivo fica em _status_mov
    ("CONCLUIDO", "TIMEOUT", "INTERROMPIDO") e a duracao em _duracao_mov.
    """
    global _status_mov, _duracao_mov

    _status_mov = "INTERROMPIDO"
    _duracao_mov = 0

    if not verificar_competicao():
        return False

    timeout = int(timeout)
    if timeout <= 0:
        # Sem tempo para nem comecar: nada e comandado.
        _status_mov = "TIMEOUT"
        return False

    relogio = StopWatch()
    concluiu = False

    try:
        mL.run_angle(velocidade, graus_l, then=Stop.HOLD, wait=False)
        mR.run_angle(velocidade, graus_r, then=Stop.HOLD, wait=False)

        while True:
            # Conclusao e testada antes do timeout: terminar no mesmo
            # instante do limite conta como concluido.
            if mL.done() and mR.done():
                concluiu = True
                _status_mov = "CONCLUIDO"
                break

            if not verificar_competicao():
                _status_mov = "INTERROMPIDO"
                break

            if relogio.time() >= timeout:
                _status_mov = "TIMEOUT"
                break

            wait(10)
    finally:
        _duracao_mov = relogio.time()
        # Qualquer saida sem conclusao (inclusive excecao) para os motores.
        if not concluiu:
            parar()

    if concluiu and not verificar_competicao():
        _status_mov = "INTERROMPIDO"
        parar()
        return False

    return concluiu


def aprender_razao(delta_l, delta_r, deslocamento, angulo):
    """
    Valida uma medida de graus-de-roda por grau-de-giro e, se confiavel,
    mistura na razao aprendida (media movel). Retorna True se aceitou.
    Uma unica medida ruim nunca substitui a razao aprendida.
    """
    global _razao_aprendida, _razao_suspeita

    mov_l = abs(delta_l)
    mov_r = abs(delta_r)
    mov = (mov_l + mov_r) / 2

    motivo = None
    medida = 0

    if deslocamento * angulo <= 0:
        motivo = "SENTIDO_INVERTIDO"
    elif abs(deslocamento) < MIN_DESLOC_CALIBRACAO:
        motivo = "POUCO_GIRO"
    elif mov <= 0:
        motivo = "RODAS_PARADAS"
    elif abs(mov_l - mov_r) > RAZAO_ASSIMETRIA_MAX * mov:
        motivo = "ASSIMETRIA"
    else:
        medida = mov / abs(deslocamento)
        if medida < RAZAO_RODA_MIN or medida > RAZAO_RODA_MAX:
            motivo = "FORA_DOS_LIMITES"

    if motivo is not None:
        print("RAZAO REJEITADA:", motivo, "MEDIDA:", medida,
              "APRENDIDA:", _razao_aprendida)
        return False

    ref = _razao_aprendida

    if abs(medida - ref) > RAZAO_DESVIO_MAX * ref:
        # Longe do aprendido: so vale se a proxima medida concordar.
        if (
            _razao_suspeita is not None
            and abs(medida - _razao_suspeita) <= 0.15 * _razao_suspeita
        ):
            _razao_aprendida = limitar(medida, RAZAO_RODA_MIN, RAZAO_RODA_MAX)
            _razao_suspeita = None
            print("RAZAO CONFIRMADA:", _razao_aprendida)
            return True

        _razao_suspeita = medida
        print("RAZAO SUSPEITA (aguarda confirmacao):", medida,
              "APRENDIDA:", ref)
        return False

    _razao_suspeita = None
    _razao_aprendida = limitar(
        0.7 * ref + 0.3 * medida,
        RAZAO_RODA_MIN,
        RAZAO_RODA_MAX
    )
    print("RAZAO MEDIDA:", medida,
          "APRENDIDA:", _razao_aprendida)
    return True


def refinar_giro(angulo, razao):
    """
    Corrige o erro restante do giro usando a IMU como referencia.

    O tempo TOTAL (movimentos + esperas) fica dentro de TEMPO_MAX_CORRECAO:
    antes de cada correcao calcula-se o tempo restante, nao se inicia um
    movimento que nao caiba e o timeout do movimento respeita o que sobra.

    Retorna (erro_final, motivo). erro_final e None se foi interrompido.
    motivo: OK, ORCAMENTO, TENTATIVAS, TIMEOUT, SEM_EFEITO, ERRO_GRANDE,
    INTERROMPIDO.
    """

    relogio = StopWatch()
    orcamento = min(TEMPO_MAX_CORRECAO, tempo_restante())
    tentativa = 0
    sem_efeito = 0
    motivo = "OK"
    erro = angulo - hub.imu.heading()

    while True:

        if abs(erro) <= TOLERANCIA_ALVO_REFINO:
            motivo = "OK"
            break

        if abs(erro) > LIMITE_ERRO_CORRECAO:
            motivo = "ERRO_GRANDE"
            break

        if tentativa >= MAX_TENTATIVAS_CORRECAO:
            motivo = "TENTATIVAS"
            break

        sentido = 1 if erro > 0 else -1
        heading_antes = hub.imu.heading()
        erro_antes = erro

        graus = razao * abs(erro)
        if graus < MIN_GRAUS_RODA_REFINO:
            graus = MIN_GRAUS_RODA_REFINO

        velocidade = limitar(
            60 + graus * 3,
            VEL_REFINO_MIN,
            VEL_REFINO_MAX
        )

        # Orcamento global: movimento estimado + espera final tem que caber.
        restante_ms = orcamento - relogio.time()
        estimado = int(graus / velocidade * 1000) + MARGEM_MOVIMENTO_MS

        if estimado + ESPERA_ASSENTAR_GIRO > restante_ms:
            motivo = "ORCAMENTO"
            break

        timeout = min(MOV_TIMEOUT_MAX, restante_ms - ESPERA_ASSENTAR_GIRO)

        comando = sentido * graus * SINAL_GIRO
        l0 = mL.angle()
        r0 = mR.angle()

        concluiu = mover_rodas_supervisionado(
            comando, -comando, velocidade, timeout
        )
        status = _status_mov
        duracao = _duracao_mov

        real_l = mL.angle() - l0
        real_r = mR.angle() - r0

        if status == "INTERROMPIDO":
            print("REFINO", tentativa + 1, "INTERROMPIDO",
                  "CMD:", comando, "REAL:", real_l, real_r)
            return None, "INTERROMPIDO"

        # Espera o robo parar (tambem conta no orcamento) e le a IMU.
        if not esperar_controlado(ESPERA_ASSENTAR_GIRO):
            return None, "INTERROMPIDO"

        heading_depois = hub.imu.heading()
        erro = angulo - heading_depois
        tentativa += 1

        print(
            "REFINO", tentativa,
            "ALVO:", angulo,
            "HEAD:", heading_antes, ">", heading_depois,
            "ERRO:", erro_antes, ">", erro,
            "CMD:", comando, (-comando),
            "REAL:", real_l, real_r,
            "VEL:", int(velocidade),
            "DUR:", duracao, "ms",
            "RESTA:", max(0, orcamento - relogio.time()), "ms",
            "STATUS:", status
        )

        if not concluiu:
            # Timeout do movimento: motores ja foram parados e seguram a
            # posicao. Nao se aprende nada com um movimento incompleto.
            motivo = "TIMEOUT"
            break

        # Ajuste local da razao: so com movimento completo, rodas que
        # realmente andaram e avanco da IMU grande o bastante para medir.
        progresso = (heading_depois - heading_antes) * sentido
        real_medio = (abs(real_l) + abs(real_r)) / 2
        rodas_andaram = real_medio >= 0.5 * graus

        if progresso >= MIN_PROGRESSO_RAZAO and rodas_andaram:
            proporcao = progresso / abs(erro_antes)
            if 0.1 <= proporcao <= 2.5:
                razao = limitar(
                    razao * limitar(1.0 / proporcao, 0.7, 1.6),
                    RAZAO_RODA_MIN,
                    RAZAO_RODA_MAX
                )
                sem_efeito = 0
            else:
                print("RAZAO LOCAL IGNORADA: PROPORCAO", proporcao)
        else:
            # Rodas nao andaram, ou andaram e a IMU quase nao mudou
            # (derrapagem / IMU insensivel). Aumentar a razao nao ajuda.
            sem_efeito += 1
            if sem_efeito >= 2:
                motivo = "SEM_EFEITO"
                break

    print("REFINO FIM:", motivo,
          "TENTATIVAS:", tentativa,
          "ERRO:", erro,
          "TEMPO:", relogio.time(), "/", orcamento, "ms")

    return erro, motivo


def giro_interno(angulo, velocidade=45):

    if abs(angulo) < 0.1:
        parar()
        return True

    parar()
    if not esperar_imu():
        return False
    if not esperar_controlado(200):
        return False

    # Comeca a medicao no ponto em que o robo realmente esta.
    # Nao movimenta os motores para descobrir o sentido.
    hub.imu.reset_heading(0)
    if not esperar_controlado(50):
        return False

    limite_potencia = limitar(
        abs(velocidade),
        POTENCIA_MIN_GIRO,
        POTENCIA_MAX_GIRO
    )

    angulo_l_inicio = mL.angle()
    angulo_r_inicio = mR.angle()

    relogio = StopWatch()
    ultimo_tempo = relogio.time()
    ultimo_heading = hub.imu.heading()
    fase1_ok = False

    # ------------------------------------------------------------------
    # FASE 1: giro por potencia ate chegar perto do alvo.
    # ------------------------------------------------------------------
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

        # Perto o bastante: a potencia minima (25%) nao vence o atrito
        # do pivo, entao o acabamento passa para o refinamento por posicao.
        if restante <= FIM_FASE_DC:
            fase1_ok = True
            break

        sentido_erro = 1 if erro > 0 else -1
        taxa_na_direcao = taxa * sentido_erro

        # Perfil em etapas: rapido longe do alvo e mais lento na aproximacao.
        if restante > 35:
            potencia = limite_potencia
        elif restante > 15:
            potencia = max(
                POTENCIA_MIN_GIRO,
                int(limite_potencia * 0.75)
            )
        else:
            potencia = max(
                POTENCIA_MIN_GIRO,
                int(limite_potencia * 0.60)
            )

        # Se a inercia ja estiver levando o robo ao alvo muito rapido,
        # aplica torque contrario para frear em vez de continuar acelerando.
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

    parar()
    if not esperar_controlado(ESPERA_ASSENTAR_GIRO):
        return False

    # ------------------------------------------------------------------
    # FASE 2: refinamento por posicao, conferido pela IMU.
    # A razao roda/giro vem da fase 1 deste giro, mas so entra na razao
    # aprendida se a medida for confiavel (ver aprender_razao).
    # ------------------------------------------------------------------
    if fase1_ok:
        aprender_razao(
            mL.angle() - angulo_l_inicio,
            mR.angle() - angulo_r_inicio,
            hub.imu.heading(),
            angulo
        )
    else:
        print("RAZAO NAO APRENDIDA: FASE 1 SEM CONCLUIR (TIMEOUT)")

    erro_refino, motivo_refino = refinar_giro(angulo, _razao_aprendida)

    if erro_refino is None:
        # Interrompido (CENTER / 150 s): motores ja parados, sem registro.
        parar()
        return False

    parar()

    # O refino ja esperou o robo assentar antes da ultima leitura.
    angulo_real = hub.imu.heading()
    erro_final = angulo - angulo_real

    print("GIRO ALVO:", angulo)
    print("GIRO REAL:", angulo_real)
    print("ERRO FINAL:", erro_final)

    if not verificar_competicao():
        return False

    if abs(erro_final) > TOLERANCIA_GIRO:
        print("GIRO NAO ATINGIU A TOLERANCIA:", motivo_refino)
        registrar_falha()
        return False

    registrar_sucesso()
    return True


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
    # Alias explicito: diferente de parar(), que apenas segura as rodas.
    solicitar_parada()
    parar()
    parar_garras()
    return True


# ==========================================
# CONSULTAR APRENDIZADO
# ==========================================

def mostrar_aprendizado():

    print("======================")
    print("RABBITECH AUTOPILOT V3.3")
    print("======================")

    print("MEMORIA FRENTE:", memoria_frente)
    print("MEMORIA RE:", memoria_re)

    print("MOVIMENTOS OK:", movimentos_concluidos)
    print("MOVIMENTOS COM ERRO:", movimentos_falhos)

    print("======================")
