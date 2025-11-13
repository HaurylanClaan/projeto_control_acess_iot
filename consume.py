from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import insightface
import json
import datetime
import base64
import csv

app = Flask(__name__)

LOG_FILE = "access_log.csv"
KNOWN_FACES = "known_faces.json"

# Cria o arquivo de log se não existir
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "nome", "resultado"])

# Carrega o modelo de reconhecimento facial
model = insightface.app.FaceAnalysis(providers=["CPUExecutionProvider"])
model.prepare(ctx_id=0, det_size=(640, 640))

# Carrega os rostos conhecidos
if os.path.exists(KNOWN_FACES):
    with open(KNOWN_FACES, "r") as f:
        known_faces = json.load(f)
else:
    known_faces = {}

def reconhecer_face(img_bgr):
    faces = model.get(img_bgr)
    if not faces:
        return None
    return faces[0].normed_embedding

def comparar_face(embedding, known_faces):
    if embedding is None:
        return None, 0.0
    melhor_nome = None
    maior_similaridade = 0.0
    for nome, dados in known_faces.items():
        known_emb = np.array(dados["embedding"], dtype=np.float32)
        similaridade = np.dot(embedding, known_emb)
        if similaridade > maior_similaridade:
            melhor_nome = nome
            maior_similaridade = similaridade
    return melhor_nome, maior_similaridade

@app.route("/analise", methods=["POST"])
def analise():
    """Recebe uma imagem e verifica se o rosto está cadastrado."""
    data = request.get_json()
    imagem_b64 = data.get("imagem")

    if not imagem_b64:
        return jsonify({"erro": "Imagem não enviada"}), 400

    img_bytes = base64.b64decode(imagem_b64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    embedding = reconhecer_face(img_bgr)
    nome, similaridade = comparar_face(embedding, known_faces)

    if nome and similaridade > 0.35:
        resultado = "Acesso liberado"
        acesso = True
    else:
        resultado = "Acesso negado"
        nome = "Desconhecido"
        acesso = False

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), nome, resultado])

    print(f"🔍 {nome} → {resultado} ({similaridade:.2f})")

    return jsonify({
        "acesso": acesso,
        "nome": nome,
        "similaridade": float(similaridade),
        "mensagem": resultado
    }), 200


@app.route("/cadastro", methods=["POST"])
def cadastro():
    """Cadastra uma nova pessoa com nome e imagem."""
    data = request.get_json()
    nome = data.get("nome")
    imagem_b64 = data.get("imagem")

    if not nome or not imagem_b64:
        return jsonify({"erro": "Nome e imagem são obrigatórios"}), 400

    img_bytes = base64.b64decode(imagem_b64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    embedding = reconhecer_face(img_bgr)
    if embedding is None:
        return jsonify({"erro": "Nenhum rosto detectado"}), 400

    known_faces[nome] = {"embedding": embedding.tolist()}

    with open(KNOWN_FACES, "w") as f:
        json.dump(known_faces, f, indent=4)

    print(f"✅ Novo cadastro: {nome}")
    return jsonify({"mensagem": f"{nome} cadastrado com sucesso!"}), 201


@app.route("/")
def home():
    return "Servidor de reconhecimento facial ativo!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
