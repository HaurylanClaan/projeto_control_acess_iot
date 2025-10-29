# 🧠 Sistema de Reconhecimento Facial com AMQP (RabbitMQ) e IoT

Projeto desenvolvido na disciplina **Aplicações de Cloud, IoT e Indústria 4.0 em Python**, com foco em integrar **hardware e software** usando o protocolo **AMQP (Advanced Message Queuing Protocol)** através do **RabbitMQ**.

-----------------------------------------------------------------------------------------------------------------------------------

## 📘 Visão Geral

O sistema implementa um **controle de acesso inteligente** que utiliza **reconhecimento facial** para autorizar ou negar o acesso de pessoas.  
Cada evento de reconhecimento é publicado e consumido via **RabbitMQ**, simulando o comportamento de uma aplicação **IoT distribuída**.

A arquitetura se divide em três módulos principais:

| Módulo       | Função                                                   |
|--------------|----------------------------------------------------------|
| `enroll.py`  | Captura e cadastra rostos (gera embeddings faciais).    |
| `publisher.py` | Reconhece rostos em tempo real e publica eventos AMQP. |
| `consume.py` | Recebe os eventos do RabbitMQ e registra logs de acesso.|

-----------------------------------------------------------------------------------------------------------------------------------

## 🧩 Tecnologias Utilizadas

- **Python 3.10+**
- **InsightFace (ArcFace)** — modelo de embeddings faciais (512-D)
- **OpenCV** — captura e exibição de vídeo
- **NumPy** — operações vetoriais
- **RabbitMQ** — mensageria AMQP
- **Pika** — cliente Python para RabbitMQ

-----------------------------------------------------------------------------------------------------------------------------------

### ⚙️ Estrutura do Projeto

projeto_control_acess_iot/

│
├── enroll.py # Cadastro facial
├── publisher.py # Reconhecimento + envio AMQP
├── consume.py # Consumidor RabbitMQ
├── known_faces.json # Base de rostos cadastrados
├── access_log.csv # Log dos acessos recebidos (gerado após execução)
├── requirements.txt # Dependências do projeto
└── venv/ # Ambiente virtual (não versionado)

-----------------------------------------------------------------------------------------------------------------------------------

## 🚀 Instalação e Execução

### 1️⃣ Criar o ambiente virtual
```bash
python -m venv venv

Ative o ambiente:
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/macOS

-----------------------------------------------------------------------------------------------------------------------------------

### 2️⃣ Instalar dependências
pip install -r requirements.txt

-----------------------------------------------------------------------------------------------------------------------------------

### 🐇 Subir o RabbitMQ
🔹 Opção A — via Docker (recomendado)
docker run -d --hostname rabbit --name rabbit \
  -p 5672:5672 -p 15672:15672 rabbitmq:3-management

Acesse o painel web:
👉 http://localhost:15672
Usuário: guest | Senha: guest

🔹 Opção B — instalação local
Baixe e instale o RabbitMQ em: https://www.rabbitmq.com/download.html

-----------------------------------------------------------------------------------------------------------------------------------

### 📸 Cadastrar Rostos (enroll)
Execute: python enroll.py
Digite o nome da pessoa.

Aponte o rosto para a câmera.
Pressione:
s → salva uma amostra facial.
q → encerra o cadastro.
Recomenda-se capturar 5 a 10 amostras por pessoa para robustez.
Após execução, é gerado o arquivo known_faces.json com os embeddings.

-----------------------------------------------------------------------------------------------------------------------------------

### 🧠 Executar Reconhecimento Facial (publisher)
execute: python publisher.py
Este módulo:

Captura rostos da webcam em tempo real.
Gera embeddings faciais (512-D).
Compara com os rostos cadastrados (via similaridade).
Publica evento no RabbitMQ com o resultado (Liberado ou Negado).

Exemplo de evento publicado:
{
  "person": "Bolsonaro",
  "status": "Liberado",
  "similarity": 0.41
}

-----------------------------------------------------------------------------------------------------------------------------------

### 📥 Consumir Eventos e Log (consume)
execute: python consume.py
Este módulo:

Conecta-se ao RabbitMQ na fila access_queue.
Recebe cada evento público pelo publisher.
Salva os logs no arquivo access_log.csv.

Exemplo de log no CSV:
2025-10-27 17:55:01, Felipe, Liberado, 0.41
2025-10-27 17:56:22, Desconhecido, Negado, 0.21

-----------------------------------------------------------------------------------------------------------------------------------

### 📡 Arquitetura IoT (Simplificada)
   [Câmera / Edge Device]
             │
             ▼
     ┌───────────────────────────┐
     │  publisher.py             │
     │  - Captura vídeo          │
     │  - Gera embeddings        │
     │  - Publica evento AMQP    │
     └───────────────────────────┘
             │  (AMQP)
             ▼
     ┌───────────────────────────┐
     │  RabbitMQ Broker          │
     │  - fila access_queue      │
     └───────────────────────────┘
             │
             ▼
     ┌───────────────────────────┐
     │  consume.py               │
     │  - Recebe evento          │
     │  - Grava log CSV          │
     └───────────────────────────┘

-----------------------------------------------------------------------------------------------------------------------------------

### 📈 Ajustando a Precisão

A variável THRESHOLD_SIM (no publisher.py) define a sensibilidade do reconhecimento:
| Valor   | Descrição                                  |
| ------- | ------------------------------------------ |
| `0.30`  | Mais permissivo (ringer pessoas parecidas) |
| `0.35`  | Equilíbrio perfeito para maioria dos casos |
| `0.40+` | Mais rigoroso (pode negar pessoas válidas) |

obs: Ajuste conforme a base de rostos que você capturou.

-----------------------------------------------------------------------------------------------------------------------------------

### 🛠️ Possíveis Extensões

Liveness Detection: verificar se o rosto é real (por exemplo: piscar, mover cabeça).
Exchange AMQP com tópicos:
iot.face.verified
iot.face.unknown
iot.face.alert
Dashboard (Flask ou Streamlit) para visualizar os eventos em tempo real.
Integração com hardware (Raspberry Pi + relé/LED) para liberar portas ou acionar dispositivos físicos.
Monitoramento e métricas (por exemplo: Prometheus + Grafana — taxa de reconhecimento, latência).
