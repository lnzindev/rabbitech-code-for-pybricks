from base import andar, esperar, girar, verificar_competicao

CONFIGURADA = True


def executar():
    print("SAIDA 1")
    falha_local = False

    # Falhas locais sao registradas, mas nao encerram a rodada.
    # O roteiro tenta executar as proximas etapas cadastradas.
    if not andar(200, 60):
        if not verificar_competicao():
            return False
        falha_local = True
        print("FALHA LOCAL: AVANCO. TENTANDO PROXIMA ETAPA.")

    if not esperar(500):
        return False

    if not andar(-200, 60):
        if not verificar_competicao():
            return False
        falha_local = True
        print("FALHA LOCAL: RECUO. TENTANDO PROXIMA ETAPA.")

    if not esperar(500):
        return False

    if not girar(90, 45):
        if not verificar_competicao():
            return False
        falha_local = True
        print("FALHA LOCAL: GIRO. PROXIMAS SAIDAS SERAO MANTIDAS.")

    if not verificar_competicao():
        return False

    return not falha_local
