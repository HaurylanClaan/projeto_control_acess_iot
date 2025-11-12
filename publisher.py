# publisher.py
import cv2
import json
import numpy as np
import requests
from insightface.app import FaceAnalysis
import os

DB_PATH = "known_faces.json"
THRESHOLD_SIM = 0.35  # sim >= 0.35 => mesmo rosto
API_URL = os.getenv("API_URL", "http://localhost:8000/event")  # muda fácil p/ nuvem

# Carrega base de rostos conhecidos
with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

names, centroids = [], []
for name, data in db.items():
    if isinstance(data, dict) and "centroid" in data:
        names.append(name)
        centroids.append(np.array(data["centroid"], dtype=np.float32))
centroids = np.stack(centroids, axis=0) if centroids else np.zeros((0, 512), dtype=np.float32)

# Inicializa modelo InsightFace
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))

cap = cv2.VideoCapture(0)
print("📷 Reconhecimento iniciado. Pressione 'q' para sair.")

while True:
    ok, frame = cap.read()
    if not ok:
        continue

    faces = app.get(frame)
    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        emb = face.normed_embedding
        if emb is None or centroids.shape[0] == 0:
            name, status, sim = "Desconhecido", "Negado", None
        else:
            sims = centroids @ emb.astype(np.float32)
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            if best_sim >= THRESHOLD_SIM:
                name, status, sim = names[best_idx], "Liberado", best_sim
            else:
                name, status, sim = "Desconhecido", "Negado", best_sim

        event = {
            "person": name,
            "status": status,
            "similarity": round(sim, 4) if sim is not None else None,
        }

        # Envia evento via HTTP
        try:
            r = requests.post(API_URL, json=event, timeout=2)
            if r.status_code != 200:
                print(f"⚠ Erro ao enviar evento ({r.status_code}): {r.text}")
        except Exception as e:
            print("⚠ Falha de conexão com servidor:", e)

        # Mostra na tela
        color = (0, 200, 0) if status == "Liberado" else (0, 0, 255)
        label = f"{name} - {status}" + (f" ({sim:.2f})" if sim is not None else "")
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        print("📨 Evento:", event)

    cv2.imshow("Reconhecimento Facial", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()