from base import andar, esperar, girar, verificar_competicao


def executar():
    print("SAIDA 1")

    # Cada falha e registrada, mas nao encerra a saida inteira.
    # As proximas etapas do roteiro continuam enquanto a rodada estiver ativa.
    if not andar(200, 60):
        if not verificar_competicao():
            return False
        print("FALHA LOCAL: AVANCO. TENTANDO PROXIMA ETAPA.")

    if not esperar(500):
        return False

    if not andar(-200, 60):
        if not verificar_competicao():
            return False
        print("FALHA LOCAL: RECUO. TENTANDO PROXIMA ETAPA.")

    if not esperar(500):
        return False

    if not girar(90, 45):
        if not verificar_competicao():
            return False
        print("FALHA LOCAL: GIRO. SAIDA SERA CONSIDERADA COM FALHA.")

    return verificar_competicao()
