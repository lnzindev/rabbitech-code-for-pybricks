<div align="center">

<img src="assets/rabbitech-banner.svg" alt="Rabbitech — Robótica, programação e inovação em João Pessoa, Paraíba" width="100%" />

### ROBÓTICA • PROGRAMAÇÃO • ENGENHARIA • INOVAÇÃO

**Desenvolvido por Luiz Narciso, Arthur, Nayon, Eduarda, Fernanda e Nayane.**

[Repositório](https://github.com/lnzindev/rabbitech-code-for-pybricks) · [Perfil do desenvolvedor](https://github.com/lnzindev) · [Outros projetos Rabbitech](https://github.com/lnzindev?tab=repositories)

![Python](https://img.shields.io/badge/Python-Pybricks-101b2d?style=for-the-badge&logo=python&logoColor=4cc9f0)
![LEGO](https://img.shields.io/badge/LEGO-SPIKE%20Prime-101b2d?style=for-the-badge)
![Robótica](https://img.shields.io/badge/Área-Robótica-101b2d?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-101b2d?style=for-the-badge)

</div>

---

## 🤖 Sobre o projeto

O **Rabbitech Pybricks Autopilot** é um projeto de programação e controle robótico para o LEGO SPIKE Prime, desenvolvido por **Luiz Narciso**, em João Pessoa, Paraíba.

A proposta é transformar estratégias e ideias em movimentos reais: controlar motores, executar rotinas, realizar giros com auxílio da IMU e registrar dados para aprimorar o comportamento do robô.

Este repositório faz parte da trajetória de experimentação em robótica da Rabbitech. Mais do que reunir códigos, ele documenta o desenvolvimento de soluções, testes e melhorias.

## ⚡ Recursos do sistema

- **Controlador sequencial:** organiza até oito rotinas em uma única execução.
- **Controle de direção:** utiliza a IMU para corrigir o alinhamento durante os deslocamentos.
- **Movimento adaptativo:** mantém valores de correção que podem ser reaproveitados em execuções futuras.
- **Rampas de velocidade:** permite aceleração e desaceleração progressivas.
- **Sistema de giros:** oferece giros com duas rodas ou com apenas uma roda.
- **Monitoramento dos motores:** identifica situações em que um motor deixa de responder durante o movimento.
- **Memória persistente:** registra estatísticas e parâmetros adaptativos no armazenamento do hub.
- **Controle das garras:** permite comandar os mecanismos esquerdo e direito separadamente.

## 🧩 Organização dos arquivos

| Arquivo | Função |
|---|---|
| `main.py` | Controlador principal. Coordena as oito rotinas. |
| `base.py` | Configuração do hardware, movimentos, giros, garras e memória adaptativa. |
| `memoria.py` | Script de teste para salvar e recuperar os dados de aprendizado. |
| `saida_1.py` a `saida_8.py` | Rotinas individuais executadas pelo controlador. |

## 🔌 Configuração do robô

A configuração atual de `base.py` utiliza as seguintes portas:

| Porta | Componente |
|---|---|
| C | Motor da garra esquerda |
| D | Motor da garra direita |
| E | Motor de tração esquerdo |
| F | Motor de tração direito |

| Parâmetro | Configuração atual |
|---|---|
| Hub | LEGO SPIKE Prime |
| Diâmetro das rodas | 56 mm |
| Ambiente | Pybricks MicroPython 3.6.1 |

Confira as conexões físicas, o sentido de rotação e a montagem antes de executar o programa. Caso o robô utilize outra configuração, ajuste as definições no arquivo `base.py`.

## 🧠 Como funciona

1. O hub inicializa os motores e tenta recuperar os dados adaptativos salvos.
2. O controlador aguarda a IMU ficar pronta e interrompe o movimento dos motores de tração.
3. O visor mostra o número da próxima saída.
4. O usuário aperta e solta o **botão esquerdo** do hub para iniciar a rotina.
5. A rotina é executada e, ao terminar, o controlador para os motores.
6. Se uma rotina retornar `False`, a sequência é interrompida e o visor mostra um erro.
7. Se todas forem concluídas, o visor apresenta `FIM`.

## ▶️ Como executar

1. Prepare o hub LEGO SPIKE Prime com firmware compatível com Pybricks.
2. Abra os arquivos no editor de código do Pybricks.
3. Transfira os módulos necessários para o hub.
4. Execute **`main.py`**, que é o ponto de entrada do projeto.
5. Posicione o robô em uma área segura e use o botão esquerdo para iniciar cada rotina.

> **Segurança:** teste cada rotina separadamente, em uma área livre e controlada. Verifique a direção dos motores, a fixação das peças e o movimento das garras antes de executar a sequência completa.

## 🛠️ Personalização

As configurações principais estão centralizadas em `base.py`:

- Velocidades de deslocamento e giro.
- Velocidade e ângulos das garras.
- Diâmetro das rodas.
- Parâmetros de correção de direção.
- Tolerância e tempo limite dos giros.
- Limites da memória adaptativa.

Faça alterações gradualmente e valide cada mudança no robô físico.

## 🚧 Estado atual e próximos passos

O projeto está em desenvolvimento. No estado atual do repositório, os arquivos `saida_1.py` a `saida_8.py` ainda contêm a mesma sequência de movimentos de exemplo. Cada arquivo precisa receber sua rotina definitiva antes de ser utilizado em uma apresentação ou competição.

Outros objetivos de evolução:

- Documentar cada rotina e sua missão correspondente.
- Registrar resultados dos testes de movimento.
- Melhorar a calibração dos giros e deslocamentos.
- Evoluir o sistema de memória adaptativa.
- Manter o código modular, legível e fácil de manter.

## 🏆 Robótica em João Pessoa

A robótica educacional de João Pessoa tem conquistado espaço em competições e projetos de tecnologia. Em fevereiro de 2026, a Prefeitura de João Pessoa publicou os resultados da etapa regional da FIRST LEGO League Challenge 2025/2026, destacando a equipe **Tech Scorpions**, da Escola Municipal Antônio Santos Coelho Neto, com o 1º lugar em Core Values e o 3º lugar em Desempenho do Robô.

Luiz Narciso dos Santos Oliveira aparece entre os integrantes da equipe na publicação oficial. Essa trajetória representa o espírito que inspira este projeto: colaboração, criatividade, programação e vontade de construir soluções.

**Fonte:** [Prefeitura de João Pessoa — resultados da FIRST LEGO League Challenge 2025/2026](https://www.joaopessoa.pb.gov.br/noticias/rede-municipal-de-ensino-de-joao-pessoa-e-a-unica-do-brasil-a-conquistar-tres-categorias-da-first-lego-league-challenge-2025-2026/).

---

<div align="center">

## RABBITECH

**Da ideia ao código. Do código ao movimento.**

Desenvolvido por **Luiz Narciso, Arthur, Nayon, Eduarda, Fernanda e Nayane** · João Pessoa, Paraíba, Brasil.

[GitHub](https://github.com/lnzindev) · [Ver repositório](https://github.com/lnzindev/rabbitech-code-for-pybricks)

<sub>Construir. Testar. Aprender. Evoluir.</sub>

</div>
