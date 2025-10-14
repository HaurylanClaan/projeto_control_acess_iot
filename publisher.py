import cv2
import mediapipe as mp
import numpy as np
import pika #kkkkkkk
import json

# carreg os rosto ja cadastrado
with open("known_faces.json", "r") as f:
    known_faces = json.load(f)

mp_face = mp.solutions.face_detection
cap = cv2.VideoCapture(0)

# confiuração do rabbit
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='access_queue')

def compare_face(face_encoding):
    for name, known_encoding in known_faces.items():
        distance = np.linalg.norm(np.array(known_encoding) - np.array(face_encoding))
        if distance < 50:
            return name
    return None

with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb)
#poha
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)

                # desenha retanggulo no rosto
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                face_img = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
                face_encoding = np.mean(face_img, axis=(0,1)).tolist()
                person = compare_face(face_encoding)
                status = "Liberado" if person else "Negado"
                event = {"person": person if person else "Desconhecido", "status": status}
                
                # Eenvia pra o rabbit mq 
                channel.basic_publish(exchange='', routing_key='access_queue', body=json.dumps(event))
                
                # mostra status na tela
                cv2.putText(frame, f"{person if person else 'Desconhecido'} - {status}", 
                            (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                
                print(event)

        # agora presto essa poha da camera
        cv2.imshow("Reconhecimento Facial", frame) # inicia a camera

        # Sai com q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
connection.close()
