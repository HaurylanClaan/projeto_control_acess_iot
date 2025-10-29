# publisher.py
import cv2
import json
import numpy as np
import pika
from insightface.app import FaceAnalysis

DB_PATH = "known_faces.json"
RABBIT_HOST = "localhost"
QUEUE_NAME = "access_queue"
THRESHOLD_SIM = 0.35  # sim >= 0.35 => mesmo rosto (ajuste conforme seus dados)

# Carrega base
with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

names, centroids = [], []
for name, data in db.items():
    if isinstance(data, dict) and "centroid" in data:
        names.append(name)
        centroids.append(np.array(data["centroid"], dtype=np.float32))
centroids = np.stack(centroids, axis=0) if centroids else np.zeros((0, 512), dtype=np.float32)

# InsightFace
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))

# RabbitMQ (fila durável)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

def publish(event: dict):
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)  # persistente
    )

cap = cv2.VideoCapture(0)
print("Reconhecimento iniciado. Pressione 'q' para sair.")

while True:
    ok, frame = cap.read()
    if not ok:
        continue

    faces = app.get(frame)
    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        emb = face.normed_embedding  # [512], L2-normalizado
        if emb is None or centroids.shape[0] == 0:
            name, status, sim = "Desconhecido", "Negado", None
        else:
            # similaridade por produto interno (como é L2-normalizado = cosseno)
            sims = centroids @ emb.astype(np.float32)
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            if best_sim >= THRESHOLD_SIM:
                name, status, sim = names[best_idx], "Liberado", best_sim
            else:
                name, status, sim = "Desconhecido", "Negado", best_sim

        event = {"person": name, "status": status, "similarity": round(sim, 4) if sim is not None else None}
        publish(event)
        print("Evento:", event)

        color = (0, 200, 0) if status == "Liberado" else (0, 0, 255)
        label = f"{name} - {status}" + (f" ({sim:.2f})" if sim is not None else "")
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Reconhecimento Facial", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
connection.close()
