from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuração do Webhook no Kommo
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")  # URL correta do webhook no Kommo
KOMMO_TOKEN = os.getenv("KOMMO_API_TOKEN")  # Token de autenticação

@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    try:
        logging.info("Recebendo requisição do webhook do Kommo")
        logging.info(f"Content-Type recebido: {request.content_type}")
        
        # Obtém o corpo da requisição considerando o Content-Type
        if request.content_type == "application/json":
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        logging.info(f"Dados recebidos: {data}")
        
        # Verifica se há uma mensagem válida no payload
        if not data or "message[add][0][text]" not in data:
            logging.warning("Mensagem vazia recebida ou dados inválidos")
            return jsonify({"error": "Mensagem vazia recebida"}), 400
        
        # Extrai as informações necessárias
        message_text = data.get("message[add][0][text]")
        chat_id = data.get("message[add][0][chat_id]")
        contact_id = data.get("message[add][0][contact_id]")
        talk_id = data.get("message[add][0][talk_id]")
        
        if not all([chat_id, contact_id, talk_id]):
            logging.error("Campos obrigatórios ausentes no payload")
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400
        
        logging.info(f"Mensagem recebida: {message_text}")
        
        # Resposta automática da Luiza
        response_text = "Olá! Como posso te ajudar hoje? 😊"
        
        # Monta o payload da resposta
        payload = {
            "message": [
                {
                    "chat_id": chat_id,
                    "contact_id": contact_id,
                    "talk_id": talk_id,
                    "text": response_text,
                    "type": "outgoing"
                }
            ]
        }
        
        # Cabeçalhos corretos
        headers = {
            "Authorization": f"Bearer {KOMMO_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Envia a resposta ao Webhook configurado no Kommo
        logging.info(f"Enviando resposta ao Kommo: {payload}")
        response = requests.post(KOMMO_WEBHOOK_URL, json=payload, headers=headers)
        
        logging.info(f"Resposta do Kommo: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            return jsonify({"success": "Mensagem enviada com sucesso"}), 200
        else:
            return jsonify({"error": f"Erro ao enviar mensagem: {response.text}"}), response.status_code

    except Exception as e:
        logging.exception("Erro interno ao processar o webhook")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
