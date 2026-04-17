# Pysteroids - Projeto de Sistemas Distribuídos (SD)

## Descrição do Projeto
Este projeto consiste num jogo multiplayer (Asteroids) desenvolvido em **Python**, recorrendo à biblioteca **ZeroMQ (ZMQ)** para a gestão de rede e ao **Pygame** para a componente gráfica. A nossa abordagem foca-se num modelo de **servidor autoritário**, onde toda a lógica de jogo e física é processada centralmente para garantir a consistência entre todos os jogadores.

---

## Respostas aos Critérios de Avaliação Intermédia

Para esta fase do projeto, focámo-nos em cumprir os requisitos fundamentais de comunicação e estrutura de dados, conforme detalhado abaixo:

### (a) Comunicação entre Servidor e Múltiplos Clientes
> **Questão:** *Ter a comunicação a funcionar com mais do que um cliente. Ter a possibilidade de existir comunicação entre o servidor e pelo menos dois clientes.*

**Resposta e Justificação:**
Implementámos uma infraestrutura que suporta múltiplos clientes de forma assíncrona. O servidor utiliza o `zmq.Poller()` para "escutar" todos os clientes ligados sem interromper o ciclo de física do jogo. Cada cliente, ao iniciar, gera um identificador único (ID) que é enviado em todas as mensagens, permitindo ao servidor gerir naves e pontuações de forma independente para cada utilizador. Atualmente, o sistema suporta confortavelmente 4 ou mais jogadores em simultâneo.

### (b) Protocolos e Tipos de Comunicação
> **Questão:** *Protocolos e tipos de comunicação estabelecida entre os diferentes elementos do sistema, justificando a sua escolha. Devem responder às questões:*
> - *Que informação é enviada por cada jogador?*
> - *Que informação é devolvida pelo servidor?*

**Resposta e Justificação:**
Optámos por utilizar o protocolo **ZeroMQ** com mensagens serializadas em **JSON**. Escolhemos o JSON pela sua leveza e facilidade de leitura (humana e por código), o que simplifica a depuração de mensagens em tempo real.
- **Que informação é enviada por cada jogador?** O cliente envia mensagens de `connect` (ligação inicial) e mensagens de `input`. Nestas últimas, enviamos apenas o estado das teclas que o utilizador está a pressionar (ex: setas e espaço), evitando o envio desnecessário de coordenadas do lado do cliente.
- **Que informação é devolvida pelo servidor?** O servidor utiliza um padrão de **Broadcast (PUB/SUB)**. Devolve o estado global do jogo (posições de todos os asteroides, naves, lasers e as respetivas pontuações) para todos os clientes subscritos. Isto garante que todos os jogadores vejam o mesmo estado de jogo ao mesmo tempo.

### (c) Máquina de Jogo, Estrutura e Base de Dados
> **Questão:** *A máquina de jogo, na parte do servidor com a estrutura e a base de dados devem estar implementadas.*

**Resposta e Justificação:**
O real estado do jogo reside inteiramente no servidor. Implementámos uma estrutura de dados robusta baseada em dicionários que atua como a nossa base de dados em memória.
- **Estrutura:** Cada entidade (nave, asteroide, laser) é representada por um dicionário com propriedades de posição (`x`, `y`), velocidade (`vx`, `vy`) e raio (`r`) para o cálculo de colisões.
- **Física:** O servidor processa o movimento ilimitado (wrap-around) para que nada saia do ecrã, a fricção das naves e a deteção de colisões circular. Quando um laser atinge um asteroide, o servidor decide a divisão deste em pedaços menores e atualiza a pontuação do jogador correspondente.

---

## Como Executar o Código

### 1. Instalar as Dependências
Certifique-se de que tem o Python instalado e corra:
```bash
pip install pyzmq pygame
```

### 2. Iniciar o Servidor
O servidor deve ser o primeiro a ser iniciado:
```bash
python server.py
```

### 3. Iniciar os Clientes
Pode iniciar vários clientes em janelas diferentes para testar o modo multiplayer:
```bash
python client.py [ip_do_servidor]
```
*Nota: Utilize as teclas de setas para movimentação e a barra de ESPAÇO para disparar.*

---

## Estado de Desenvolvimento (Lista de Tarefas)
- [x] Implementação da interface gráfica em Pygame.
- [x] Sistema de rede PUB/SUB para transmissão de estado.
- [x] Mecânicas de disparo e gestão de lasers.
- [x] Deteção de colisões (Nave-Asteroide e Laser-Asteroide).
- [x] Divisão dinâmica de asteroides.
- [x] Implementação de recuo e fricção da nave.
- [ ] Adicionar modos de jogo competitivos (PvP) e cooperativos (PvE).
- [ ] Implementar uma tabela de recordes persistente.
- [ ] Adicionar efeitos sonoros e visuais (partículas).
- [ ] Criar um menu inicial intuitivo.
- [ ] Implementar power-ups
