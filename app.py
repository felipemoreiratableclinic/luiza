from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Configuração da OpenAI API Key
OPENAI_API_KEY = "SUA_CHAVE_OPENAI_AQUI"
openai.api_key = OPENAI_API_KEY

# URL do Webhook do Kommo
KOMMO_WEBHOOK_URL = "SUA_URL_DO_WEBHOOK_DO_KOMMO_AQUI"

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

        # Enviar resposta ao Kommo
        response_payload = {
            "lead_id": lead_id,
            "message": reply
        }
        requests.post(KOMMO_WEBHOOK_URL, json=response_payload)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000)
