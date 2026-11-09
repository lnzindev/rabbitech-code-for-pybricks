# Rabbitech — memória persistente
# Copyright (c) 2026 Rabbitech contributors.
ASSINATURA = b"RBT3"
TAMANHO_MEMORIA = 12

def codificar_16(valor):
    valor = max(0, min(65535, int(valor)))
    return bytes((valor // 256, valor % 256))

def decodificar_16(dados, posicao):
    return dados[posicao] * 256 + dados[posicao + 1]

def codificar_memoria(valor):
    return codificar_16(max(-7000, min(7000, int(valor * 1000))) + 32768)

def decodificar_memoria(dados, posicao):
    return (decodificar_16(dados, posicao) - 32768) / 1000

def salvar(hub, frente, re, concluidos, falhos):
    dados = ASSINATURA + codificar_memoria(frente) + codificar_memoria(re) + codificar_16(concluidos) + codificar_16(falhos)
    try:
        hub.system.storage(0, write=dados)
        return True
    except Exception as erro:
        print("ERRO AO SALVAR MEMORIA:", erro)
        return False

def carregar(hub):
    try:
        dados = hub.system.storage(0, read=TAMANHO_MEMORIA)
        if len(dados) != TAMANHO_MEMORIA or dados[:4] != ASSINATURA:
            return (0.0, 0.0, 0, 0)
        return (decodificar_memoria(dados, 4), decodificar_memoria(dados, 6), decodificar_16(dados, 8), decodificar_16(dados, 10))
    except Exception as erro:
        print("ERRO AO LER MEMORIA:", erro)
        return (0.0, 0.0, 0, 0)
