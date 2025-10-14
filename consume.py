# essa aplicação é o publisher que 
import pika
import json
import csv
from datetime import datetime
#ox conexão do pika kkkk comm o rabbitmq
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='access_queue')

def callback(ch, method, properties, body):
    event = json.loads(body)
    print("Evento recebido:", event)
    with open("access_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event["person"], event["status"]])

channel.basic_consume(queue='access_queue', on_message_callback=callback, auto_ack=True)
print("Esperando eventos...")
channel.start_consuming()
