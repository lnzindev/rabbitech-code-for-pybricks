# Autoria e proteção de código — Rabbitech Pybricks

## Verificação única de integridade

O projeto possui um único verificador: `tools/integrity.py`.
O arquivo `integrity_manifest.json` é apenas a lista de hashes aprovados, não um segundo programa.

No computador, na raiz do repositório:

```bash
python tools/integrity.py verify
```

Depois de uma alteração legítima e revisada:

```bash
python tools/integrity.py update
python tools/integrity.py verify
```

A automação do GitHub executa a verificação nos pushes e pull requests para `main`. Os arquivos antigos `security.py` e `tools/update_integrity.py` foram removidos para não manter verificadores duplicados ou falsos.

## Limites técnicos no Pybricks

O programa do Hub não relê os arquivos-fonte instalados para conferir seus hashes em tempo de execução. A verificação ocorre no computador e no GitHub, antes da publicação. Isso detecta mudanças não acompanhadas no repositório oficial, mas não impede que alguém copie um repositório público, altere a cópia e gere outro manifesto.

Para restringir acesso ao fonte, mantenha o repositório de desenvolvimento privado e distribua apenas o necessário. Preserve commits, tags e registros de autoria.

## Segurança do robô

A proteção não apaga a memória do Hub, não danifica motores e não bloqueia permanentemente o dispositivo.
