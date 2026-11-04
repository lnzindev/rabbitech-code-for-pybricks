
from base import (
    memoria_frente,
    memoria_re,
    movimentos_concluidos,
    movimentos_falhos,
    salvar_aprendizado,
    carregar_aprendizado,
    mostrar_aprendizado
)

print("TESTE DE MEMORIA RABBITECH")

# Mostrar memoria inicial
mostrar_aprendizado()

# Salvar os dados
print("SALVANDO...")
salvar_aprendizado()

# Recuperar os dados
print("RECUPERANDO...")
carregar_aprendizado()

# Mostrar novamente
mostrar_aprendizado()

print("TESTE FINALIZADO")
