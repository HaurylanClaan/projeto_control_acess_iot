import cv2
import mediapipe as mp
import numpy as np
import json
import os

# inicializa Mmdiapipe e openCV
mp_face = mp.solutions.face_detection
cap = cv2.VideoCapture(0)

# carrega a poha da base exixttente
if os.path.exists("known_faces.json"):
    with open("known_faces.json", "r") as f:
        known_faces = json.load(f)
else:
    known_faces = {}

print("🔹 pressione 's' para salvar o rosto detectado.")
print("🔹 presione 'q' para sair.")

with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb)

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)

                # desenha retangulo envolta do rosto
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(frame, "Rosto detectado", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                face_img = frame[y1:y2, x1:x2]

                # salv se aperta s
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    name = input("digite o nome da pessoa: ").strip()
                    if name:
                        encoding = np.mean(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB), axis=(0,1)).tolist()
                        known_faces[name] = encoding
                        with open("known_faces.json", "w") as f:
                            json.dump(known_faces, f, indent=4)
                        print(f"✅ rosto de {name} salvo com sucesso")
                    else:
                        print("⚠️ nome invalido, tente novamente.")
                elif key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

        cv2.imshow("cadastro facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

# salva essa poha ao sair
with open("known_faces.json", "w") as f:
    json.dump(known_faces, f, indent=4)

print("adastro encerrado.")
