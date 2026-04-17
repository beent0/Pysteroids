# Pysteroids - Jogo de Sistemas Distribuídos (SD)

## Descrição do Projeto
Este projeto consiste num jogo multiplayer (Asteroids) desenvolvido em **Python**, utilizando **sockets TCP puros (Raw TCP)** para a gestão de rede e a biblioteca **Pygame** para a componente gráfica. A arquitetura baseia-se num modelo de **servidor autoritário**, onde toda a lógica de jogo e física é processada centralmente para garantir a consistência entre todos os jogadores.

---

## Detalhes Técnicos e Critérios de Avaliação

### (a) Comunicação entre Servidor e Múltiplos Clientes
Implementámos uma infraestrutura que suporta múltiplos clientes de forma concorrente utilizando `threading`. O servidor aceita ligações TCP e cria uma thread dedicada para cada cliente, permitindo a gestão independente de naves e pontuações. O sistema suporta múltiplos jogadores em simultâneo de forma eficiente através de uma gestão thread-safe de sockets.

### (b) Protocolos e Tipos de Comunicação
A comunicação é estabelecida via **Sockets TCP** com um protocolo de aplicação customizado para garantir integridade e performance.

**1. Estrutura do Pacote:**
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
    *Enviado apenas quando há comandos ativos para otimizar o tráfego.*
    ```json
    {
      "type": "input",
      "player_id": "a1b2c3d4",
      "keys": ["left", "up", "fire"]
    }
    ```

*   **Servidor -> Cliente (Broadcast do Estado Global):**
    *Enviado a 60 FPS para garantir fluidez visual em todos os clientes.*
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
      ],
      "winner": null
    }
    ```

### (c) Máquina de Jogo e Estrutura Modular
O projeto utiliza uma arquitetura modular para separação clara de responsabilidades:

- **`common/`**: Utilitários de rede para comunicação baseada em pacotes prefixados.
- **`servidor/`**:
    - **`dados/dados.py`**: Gestor de estado (Base de Dados em memória) e motor de física.
    - **`gestor/maquina.py`**: Orquestrador de rede e aceitação de conexões.
    - **`gestor/processa_cliente.py`**: Thread de tratamento de comandos individuais (Unicast).
    - **`gestor/thread_broadcast.py`**: Thread de atualização de física e distribuição de estado global (Broadcast).
- **`cliente/`**:
    - **`broadcast_receiver.py`**: Recetor assíncrono de atualizações de rede.
    - **`interface/interface.py`**: Motor gráfico e controlador de inputs.

---

## Como Executar o Código

### 1. Instalar as Dependências
```bash
pip install pygame
```

### 2. Iniciar o Servidor
```bash
python3 -m servidor
```

### 3. Iniciar os Clientes
```bash
python3 -m cliente [ip_do_servidor] [--debug]
```
*Nota: Utilize as SETAS para movimento e ESPAÇO para disparar.*
