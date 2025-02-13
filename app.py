import os
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Pegando as chaves das variáveis de ambiente (NÃO DEIXE EXPOSTAS NO CÓDIGO)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")

# Configuração correta da OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Função para gerar resposta da IA
def get_chatgpt_response(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é Luiza, assistente digital da equipe Evelyn Liu. Responda de forma acolhedora e humanizada, sem se passar pela Evelyn, e guie os leads para o VIP 21D ou consultas na Table Clinic."},
                {"role": "user", "content": message}
            ],
            timeout=10  # Timeout de 10 segundos para evitar problemas
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🔥 Erro ao gerar resposta da OpenAI: {e}")
        return "Desculpe, estou enfrentando dificuldades técnicas no momento."

# Rota do Webhook do Kommo
@app.route("/kommo-webhook", methods=["POST", "GET"])
def kommo_webhook():
    try:
        data = request.json
        print(f"📩 Recebendo dados do Kommo: {data}")

        user_message = data.get("message", "")
        lead_id = data.get("lead_id", "")

        if not user_message:
            print("🚨 Mensagem vazia recebida!")
            return jsonify({"error": "Mensagem vazia recebida"}), 400

        # Gerar resposta da IA
        reply = get_chatgpt_response(user_message)

        print(f"📝 Resposta gerada: {reply}")

        # Enviar resposta ao Kommo
# Enviar resposta ao Kommo
response_payload = {
    "lead_id": lead_id,
    "message": reply
}
try:
    response = requests.post(
        KOMMO_WEBHOOK_URL, 
        json=response_payload, 
        headers={"Content-Type": "application/json"},
        timeout=10  # Timeout de 10 segundos para evitar bloqueios
    )
    print(f"📤 Resposta enviada ao Kommo, status: {response.status_code}")

    if response.status_code != 200:
        return jsonify({"error": "Erro ao enviar mensagem ao Kommo", "details": response.text}), 500

    return jsonify({"reply": reply})

except requests.exceptions.Timeout:
    print("🚨 Timeout ao tentar enviar resposta ao Kommo!")
    return jsonify({"error": "Timeout ao enviar resposta ao Kommo"}), 500
except Exception as e:
    print(f"🔥 Erro ao enviar resposta ao Kommo: {e}")
    return jsonify({"error": "Erro interno ao enviar resposta ao Kommo", "details": str(e)}), 500

        response_payload = {
            "lead_id": lead_id,
            "message": reply
        }
        response = requests.post(KOMMO_WEBHOOK_URL, json=response_payload)

        print(f"📤 Resposta enviada ao Kommo, status: {response.status_code}")

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
    port = int(os.environ.get("PORT", 8080))  # Render define a porta, então pegamos dinamicamente
    app.run(host="0.0.0.0", port=port, debug=True)
