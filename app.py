import os
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Pegando as chaves das variáveis de ambiente (NÃO DEIXE EXPOSTAS NO CÓDIGO)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")

# Configuração do cliente OpenAI
import openai

client = openai.Client(api_key=OPENAI_API_KEY)


# Função para gerar resposta da IA
def get_chatgpt_response(message):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é Luiza, assistente digital da equipe Evelyn Liu. Responda de forma acolhedora e humanizada, sem se passar pela Evelyn, e guie os leads para o VIP 21D ou consultas na Table Clinic."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# Rota do Webhook do Kommo
@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    try:
        data = request.json
        user_message = data.get("message", "")
        lead_id = data.get("lead_id", "")

        if not user_message:
            return jsonify({"error": "Mensagem vazia recebida"}), 400

        # Gerar resposta da IA
        reply = get_chatgpt_response(user_message)

        # Enviar resposta ao Kommo
        response_payload = {
            "lead_id": lead_id,
            "message": reply
        }
        response = requests.post(KOMMO_WEBHOOK_URL, json=response_payload)

        if response.status_code != 200:
            return jsonify({"error": "Erro ao enviar mensagem ao Kommo", "details": response.text}), 500

        return jsonify({"reply": reply})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"🔥 ERRO DETECTADO 🔥\n{error_details}")
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500

# 🚀 ROTA DE TESTE PARA SABER SE O SERVIDOR ESTÁ NO AR
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Luiza está online e rodando!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render define a porta, então pegamos dinamicamente
    app.run(host="0.0.0.0", port=port, debug=True)
