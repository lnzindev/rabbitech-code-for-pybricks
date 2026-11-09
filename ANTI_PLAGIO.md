# Proteção de autoria e integridade — Rabbitech

- A memória persistente está isolada em `memoria.py`, sem importação circular.
- `security.py` contém verificação SHA-256 dos módulos centrais.
- Gere os hashes após fechar cada versão e copie-os para `EXPECTED`.

## Limite técnico
SHA-256 detecta alterações enquanto o manifesto e verificador permanecem confiáveis. Quem recebe e consegue editar o código também pode remover o verificador ou recalcular os hashes. A memória do Hub não é um cofre criptográfico. Não existe anti-plágio absoluto para código-fonte entregue ao destinatário.

Preserve commits e tags, mantenha a fonte original privada quando possível, registre os autores e distribua somente o necessário. A proteção não apaga dados, danifica motores ou bloqueia permanentemente o Hub.
