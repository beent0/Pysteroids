# Pysteroids - Projeto de Sistemas Distribuídos (SD) - Versão Raw TCP

## Descrição do Projeto
Este projeto consiste num jogo multiplayer (Asteroids) desenvolvido em **Python**, utilizando **sockets TCP puros (Raw TCP)** para a gestão de rede e a biblioteca **Pygame** para a componente gráfica. A arquitetura baseia-se num modelo de **servidor autoritário**, onde toda a lógica de jogo e física é processada centralmente para garantir a consistência entre todos os jogadores.

---

## Detalhes Técnicos e Critérios de Avaliação

### (a) Comunicação entre Servidor e Múltiplos Clientes
Implementámos uma infraestrutura que suporta múltiplos clientes de forma concorrente utilizando `threading`. O servidor aceita ligações TCP e cria uma thread dedicada para cada cliente, permitindo a gestão independente de naves e pontuações. O sistema suporta múltiplos jogadores em simultâneo de forma eficiente.

### (b) Protocolos e Tipos de Comunicação
A comunicação é estabelecida via **Sockets TCP** com um protocolo de aplicação customizado.

**1. Estrutura do Pacote Base:**
Para evitar problemas de fragmentação TCP, implementámos um protocolo Length-Prefixed:
- **Cabeçalho:** 8 bytes (Inteiro de 64-bits, Big Endian) indicando o tamanho do payload.
- **Payload:** String codificada em UTF-8 contendo a mensagem em formato **JSON**.

**2. Dicionário de Dados (Mensagens Trocadas):**

*   **Cliente -> Servidor (Ligação Inicial):**
    ```json
    {
      "type": "connect",
      "player_id": "a1b2c3d4"
    }
    ```

*   **Cliente -> Servidor (Input de Jogo):**
    *Enviado apenas quando há alteração no estado das teclas para poupar largura de banda.*
    ```json
    {
      "type": "input",
      "player_id": "a1b2c3d4",
      "keys": ["left", "up", "fire"]
    }
    ```

*   **Servidor -> Cliente (Broadcast do Estado Global):**
    *Enviado a 60 FPS (síncrono com a framerate).*
    ```json
    {
      "ships": {
        "a1b2c3d4": {
          "player_id": "a1b2c3d4",
          "x": 400, "y": 300,
          "vx": 0.5, "vy": -0.2,
          "angle": 90, "r": 15,
          "color": [255, 0, 0],
          "score": 150,
          "alive": true,
          "respawn_timer": 0
        }
      },
      "asteroids": [
        {
          "x": 100, "y": 150,
          "vx": 1.2, "vy": 0.8,
          "r": 40
        }
      ],
      "lasers": [
        {
          "x": 415, "y": 300,
          "vx": 10, "vy": 0,
          "r": 2,
          "life": 55,
          "player_id": "a1b2c3d4"
        }
      ]
    }
    ```

### (c) Máquina de Jogo e Estrutura (Padrão Calc 7)
O projeto foi estruturado em pacotes modulares para garantir a separação de responsabilidades:

- **`common/`**: Helpers de rede partilhados para envio/receção de objetos JSON com prefixo de tamanho.
- **`servidor/`**:
    - **`dados/dados.py`**: A "Base de Dados" em memória e lógica de física (Game Machine).
    - **`gestor/maquina.py`**: Orquestrador que aceita conexões e inicia threads.
    - **`gestor/processa_cliente.py`**: Thread que escuta comandos (TCP Unicast) de um jogador específico.
    - **`gestor/thread_broadcast.py`**: Thread que atualiza a física e envia o estado global (TCP Broadcast) a todos os clientes a 60 FPS.
    - **`gestor/lista_clientes.py`**: Gestor thread-safe da lista de sockets ativos.
- **`cliente/`**:
    - **`broadcast_receiver.py`**: Thread dedicada a receber atualizações constantes do servidor.
    - **`interface/interface.py`**: Ciclo principal do Pygame e envio de inputs.

---

## Como Executar o Código

### 1. Instalar as Dependências
Certifique-se de que tem o Python 3 instalado e execute:
```bash
pip install pygame
```

### 2. Iniciar o Servidor
Execute o pacote do servidor:
```bash
python3 -m servidor
```

### 3. Iniciar os Clientes
Execute o pacote do cliente (suporta IP opcional e modo debug):
```bash
python3 -m cliente [ip_do_servidor] [--debug]
```
*Nota: Utilize as teclas de setas para movimentação e a barra de ESPAÇO para disparar.*

---

## Road-Map (TO-DO)
- [x] Implementação da interface gráfica em Pygame.
- [x] Sistema de rede customizado sobre TCP.
- [x] Protocolo de serialização JSON com prefixo de tamanho.
- [x] Mecânicas de disparo e gestão de lasers.
- [x] Deteção de colisões (Nave-Asteroide e Laser-Asteroide).
- [x] Divisão dinâmica de asteroides.
- [ ] Adicionar modos de jogo competitivos (PvP).
- [ ] Implementar tabela de recordes persistente.
- [ ] Adicionar efeitos sonoros e visuais.
- [ ] Menu
- [ ] Power-Ups
