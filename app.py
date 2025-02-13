import os
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Configuração da OpenAI API Key
OPENAI_API_KEY = os.getenv("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")  # Pegando a chave da variável de ambiente
openai.api_key = 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

# URL do Webhook do Kommo
KOMMO_WEBHOOK_URL = os.getenv("https://luiza-assistente.onrender.com")  # Pegando a URL do Webhook do Kommo

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
        requests.post(https://luiza-assistente.onrender.com, json=response_payload)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render define a porta, então pegamos dinamicamente
    app.run(host="0.0.0.0", port=port, debug=True)  # Agora Flask escuta na porta correta
