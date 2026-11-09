# Autoria e proteção de código — Rabbitech Pybricks

## Como o Pybricks funciona neste projeto

O projeto usa módulos Python separados: `main.py`, `base.py`, `memoria.py` e
as oito saídas. O Pybricks Code inclui os módulos importados no programa
enviado ao Hub e compila o programa para execução. Isso mantém a organização
modular, mas **não protege o código-fonte que estiver publicado no GitHub**.

O Hub não oferece uma API portátil para que o programa em execução abra e
leia os arquivos-fonte originais e confira seus próprios hashes. Por isso,
não existe uma verificação de integridade real dentro de `main.py` baseada
em reler os módulos instalados. O antigo `security.py` foi marcado como
aviso legado para não ser confundido com uma trava de runtime.

Referências oficiais:
- [Pybricks: programas com vários arquivos](https://pybricks.com/pybricks-tools/cli/multi-file/)
- [Pybricks: menu com vários programas](https://pybricks.com/project/spike-hub-menu/)
- [Prime Hub: armazenamento persistente](https://docs.pybricks.com/en/v3.6.1/hubs/primehub.html)

## Verificação de integridade antes da publicação

O arquivo `integrity_manifest.json` guarda os IDs dos objetos Git aprovados
para `main.py`, `base.py`, `memoria.py` e `saida_1.py` até `saida_8.py`.

No computador, na pasta clonada do repositório:

```bash
python tools/integrity.py verify
```

Quando uma alteração de código for legítima e revisada, atualize o manifesto:

```bash
python tools/integrity.py update
python tools/integrity.py verify
```

Depois revise o diff do manifesto e publique o código e o manifesto no mesmo
commit. A automação do GitHub verifica se os arquivos correspondem ao
manifesto nos pushes e pull requests para `main`.

O identificador utilizado é o Git blob SHA-1. Ele serve para detectar
alterações não acompanhadas no repositório oficial, mas **não é uma assinatura
digital, não é DRM e não impede alguém de editar uma cópia e gerar outro
manifesto**. O histórico de commits ajuda a documentar a origem da versão
aprovada.

## O que realmente dificulta cópias

1. **Mantenha a fonte original privada.** Este repositório está público:
   qualquer pessoa pode visualizar e copiar os arquivos enquanto continuar
   público. Para restringir o acesso à fonte, é necessário tornar o repositório
   privado ou manter a fonte de desenvolvimento em um repositório privado e
   publicar apenas documentação e demonstrações.
2. **Distribua pelo Pybricks Code somente o programa necessário.** O Pybricks
   compila os módulos importados e envia o conjunto ao Hub. Isso evita entregar
   automaticamente a pasta de fontes, mas não transforma o programa compilado
   em conteúdo impossível de analisar.
3. **Preserve commits, tags e releases.** Isso mantém um histórico datado da
   evolução e ajuda a demonstrar a autoria do trabalho.
4. **Mantenha a licença e os avisos de autoria** nos arquivos e na
   documentação.

## Sobre a memória do Hub

`hub.system.storage()` é armazenamento persistente para dados do programa,
não um cofre de segredos. No SPIKE Prime há até 512 bytes; os dados podem ser
lidos e escritos pelo próprio programa e são apagados ao atualizar o firmware.
Não use esse recurso como única proteção de licença ou de autoria.

## Segurança do robô

Nenhuma proteção deste projeto apaga a memória do Hub, danifica motores ou
bloqueia permanentemente o dispositivo. Em caso de verificação de integridade
reprovada no computador, a publicação deve ser interrompida para revisão.
