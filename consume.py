# consume.py
import pika
import json
import csv
from datetime import datetime

RABBIT_HOST = "localhost"
QUEUE_NAME = "access_queue"
CSV_PATH = "access_log.csv"

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

def callback(ch, method, properties, body):
    try:
        event = json.loads(body)
        print("Evento recebido:", event)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event.get("person"),
                event.get("status"),
                event.get("similarity")
            ])
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Erro ao processar mensagem:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)

print("Esperando eventos...")
channel.start_consuming()
