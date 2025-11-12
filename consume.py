# consume.py
from flask import Flask, request, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__)
CSV_PATH = "access_log.csv"

@app.route("/event", methods=["POST"])
def receive_event():
    try:
        event = request.get_json(force=True)
        if not event:
            return jsonify({"error": "JSON vazio"}), 400

        # Garante que o arquivo existe e grava o evento
        os.makedirs(os.path.dirname(CSV_PATH) or ".", exist_ok=True)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event.get("person"),
                event.get("status"),
                event.get("similarity"),
            ])

        print("✅ Evento recebido:", event)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Erro ao processar evento:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌐 Servidor de eventos iniciado em http://localhost:8000/event")
    app.run(host="0.0.0.0", port=8000)
