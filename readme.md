# 🧠 Sistema de Reconhecimento Facial com Flask e Integração IoT via HTTP

Projeto desenvolvido na disciplina **Aplicações de Cloud, IoT e Indústria 4.0 em Python**, com foco em integrar **hardware e software** usando **comunicação HTTP**.
O reconhecimento facial é feito diretamente pelo servidor Flask, que recebe imagens enviadas via HTTP.

## 📘 Visão Geral

O sistema implementa um **controle de acesso inteligente** que utiliza **reconhecimento facial** para autorizar ou negar o acesso de pessoas.  
O processo ocorre da seguinte forma:

1. O **front-end** captura uma imagem facial (webcam ou dispositivo móvel).  
2. A imagem é enviada via **HTTP (POST)** para o servidor Flask.  
3. O servidor realiza a **análise facial** com base nos rostos cadastrados.  
4. O resultado é retornado ao front-end (liberado ou negado).

## 🧩 Tecnologias Utilizadas

- **Python 3.10+**
- **Flask** — Servidor HTTP e API REST
- **InsightFace (ArcFace)** — Modelo de reconhecimento facial
- **OpenCV (headless)** — Processamento de imagem
- **NumPy** — Operações vetoriais
- **ONNXRuntime** — Execução dos modelos
- **Pillow** — Manipulação de imagem



### ⚙️ Estrutura do Projeto
```bash
projeto_control_acess/
│
├── consume.py # Servidor Flask principal
├── known_faces.json # Banco local com rostos cadastrados
├── requirements.txt # Dependências do projeto
├── README.md # Este arquivo
└── venv/ # Ambiente virtual (não versionado)
```


## 🚀 Instalação e Execução

### 1️⃣ Criar o ambiente virtual
```bash
python -m venv venv
```
Ative o ambiente:
```bash
source venv/bin/activate   # Linux
venv\Scripts\activate      # Windows
```
### 2️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 3️⃣ Executar o servidor Flask

```bash
python consume.py
```
O servidor será iniciado em:

```bash
http://127.0.0.1:5000
```

### 📦 Dependências (requirements.txt)

- **flask**
- **insightface==0.7.3**
- **opencv-python-headless**
- **numpy<2**
- **onnxruntime**
- **pillow**


### 📡 Fluxo de Funcionamento
🧩 Fluxo Simplificado
```
sequenceDiagram
    participant F as Front-end
    participant S as Servidor Flask
    participant D as Banco de Rostos (known_faces.json)

    F->>S: Envia imagem Base64 via /analise
    S->>D: Verifica se o rosto já existe
    D-->>S: Retorna vetor correspondente (ou None)
    S-->>F: Retorna JSON {"status": "liberado" ou "negado"}
```

### 🧠 Endpoints da API
**POST /analise**

Recebe uma imagem em formato Base64 e retorna se o rosto é reconhecido.

**📥 Corpo da requisição (JSON)**
```bash
{
  "imagem": "<string_base64_da_imagem>"
}
```
**📤 Respostas**

**✅ Pessoa reconhecida**

```bash
{
  "status": "liberado",
  "mensagem": "Acesso permitido"
}
```
**✅ Pessoa não reconhecida**
```bash
{
  "status": "negado",
  "mensagem": "Rosto não encontrado no banco de dados"
}
```

### 💾 Banco de Dados Facial (known_faces.json)

O arquivo known_faces.json armazena os embeddings faciais (representações vetoriais do rosto).
Cada pessoa cadastrada possui um vetor de 512 dimensões gerado pelo InsightFace.

Exemplo:

```bash
{
  "joao_silva": [0.134, -0.248, 0.392, ...],
  "maria_oliveira": [0.244, -0.109, 0.503, ...]
}
```

### 🧩 Cadastro de Rostos

O cadastro de pessoas é realizado diretamente pelo front-end.

O front é responsável por:

Capturar uma imagem da pessoa;

Enviar o rosto cadastrado para o servidor (endpoint /cadastro — opcional);

Atualizar o banco de dados known_faces.json.

Se o rosto não estiver cadastrado, o servidor responde com “bloqueado”.


### 📈 Exemplo de Integração com o Front-End
```bash
async function enviarImagem(base64) {
  const response = await fetch("http://127.0.0.1:5000/analise", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imagem: base64 })
  });
  
  const data = await response.json();
  if (data.status === "liberado") {
    alert("✅ Acesso permitido!");
  } else {
    alert("❌ Acesso negado!");
  }
}
```
### 🧱 Arquitetura Simplificada

```bash
[Front-end Web]
    │
    │  (HTTP POST /analise)
    ▼
[Servidor Flask]
    │
    │  (Processa e compara rostos)
    ▼
[Base Local - known_faces.json]

```
### ⚙️ Ajustando a Precisão

A variável THRESHOLD_SIMILARITY define o nível de sensibilidade do reconhecimento:

Valor	Descrição
0.30	Mais permissivo (pode aceitar rostos parecidos)
0.35	Equilíbrio (recomendado)
0.40+	Mais rigoroso (pode negar rostos válidos)

### 👨‍💻 Autores

Desenvolvido por:
- 🧑‍💻 Haurylan Claan (BackEnd)
- 🧑‍💻 Felipe (BackEnd)
- 🧑‍💻 Paulo Silas (FrontEnd)
- 🧑‍💻 Nicolau (FrontEnd)
- 🧑‍💻 Francivaldo (Documentação)
- 💡 Projeto acadêmico Iot

## 📄 Licença
Este projeto é licenciado sob os termos da [Licença MIT](LICENSE).
