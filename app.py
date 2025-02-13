import os
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Pegando as chaves das variáveis de ambiente (NÃO DEIXE EXPOSTAS NO CÓDIGO)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")

# Configuração da OpenAI API Key
openai.api_key = OPENAI_API_KEY

# Função para gerar resposta da IA
def get_chatgpt_response(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é Luiza, assistente digital da equipe Evelyn Liu. Responda de forma acolhedora e humanizada, sem se passar pela Evelyn, e guie os leads para o VIP 21D ou consultas na Table Clinic."},
            {"role": "user", "content": message}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Rota do Webhook do Kommo
@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    data = request.json
    user_message = data.get("message", "")
    lead_id = data.get("lead_id", "")

    if user_message:
        reply = get_chatgpt_response(user_message)

        # Enviar resposta para o Kommo
        response_payload = {
            "lead_id": lead_id,
            "message": reply
        }
        requests.post(KOMMO_WEBHOOK_URL, json=response_payload)

    return jsonify({"reply": reply})

# 🚀 ROTA DE TESTE PARA SABER SE O SERVIDOR ESTÁ NO AR
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Luiza está online e rodando!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render define a porta, então pegamos dinamicamente
    app.run(host="0.0.0.0", port=port, debug=True)
