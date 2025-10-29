# enroll.py
import cv2
import json
import os
import numpy as np
from insightface.app import FaceAnalysis

DB_PATH = "known_faces.json"

# Carrega base existente
if os.path.exists(DB_PATH):
    with open(DB_PATH, "r", encoding="utf-8") as f:
        known_faces = json.load(f)  # {name: {"centroid":[...], "samples":[...]}}
else:
    known_faces = {}

# Inicializa InsightFace (detector + embeddings ArcFace)
app = FaceAnalysis(name="buffalo_l")  # modelo padrão (det + rec)
app.prepare(ctx_id=0, det_size=(640, 640))  # ctx_id=0 = CPU/GPU auto; no Windows normalmente CPU

cap = cv2.VideoCapture(0)
print("▶ Cadastro: digite o nome da pessoa e capture várias amostras (s). Pressione 'q' para finalizar.")
person_name = input("Nome da pessoa: ").strip()
if not person_name:
    print("Nome inválido.")
    cap.release()
    raise SystemExit(1)

samples = []

while True:
    ok, frame = cap.read()
    if not ok:
        continue

    faces = app.get(frame)  # detecta e embute
    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, "Rosto", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    cv2.imshow("Cadastro Facial", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        if not faces:
            print("⚠ Nenhum rosto encontrado.")
            continue
        # usa o rosto com maior score
        best = max(faces, key=lambda f: f.det_score)
        emb = best.normed_embedding  # vetor 512-D normalizado (L2)
        if emb is None:
            print("⚠ Falha ao gerar embedding.")
            continue
        samples.append(emb.astype(np.float32))
        print(f"✅ Amostra capturada ({len(samples)})")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if len(samples) < 5:
    print("⚠ Poucas amostras. Ideal ≥ 5–10 para robustez.")

if samples:
    arr = np.stack(samples, axis=0)  # [n, 512], já normalizado
    centroid = (arr.mean(axis=0) / np.linalg.norm(arr.mean(axis=0))).tolist()
    known_faces[person_name] = {
        "centroid": centroid,
        "samples": [s.tolist() for s in samples]
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(known_faces, f, indent=2, ensure_ascii=False)

    print(f"🎉 Cadastro de {person_name} concluído com {len(samples)} amostras.")
else:
    print("Nada a salvar.")
