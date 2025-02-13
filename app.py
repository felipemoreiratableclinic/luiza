import os
import time
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatgpt_response(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é Luiza, assistente digital da equipe Evelyn Liu. Responda de forma acolhedora e humanizada, sem se passar pela Evelyn, e guie os leads para o VIP 21D ou consultas na Table Clinic."},
                {"role": "user", "content": message}
            ],
            timeout=10  
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🔥 Erro OpenAI: {e}")
        return "Desculpe, estou enfrentando dificuldades técnicas no momento."

@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    try:
        data = request.json
        print(f"📩 Dados recebidos: {data}")

        user_message = data.get("message", "")
        lead_id = data.get("lead_id", "")

        if not user_message:
            return jsonify({"error": "Mensagem vazia recebida"}), 400

        # Gerar resposta da IA
        reply = get_chatgpt_response(user_message)
        print(f"📝 Resposta da IA: {reply}")

        response_payload = {
            "lead_id": lead_id,
            "message": reply
        }

        # Medir tempo de resposta do Kommo
        start_time = time.time()
        try:
            response = requests.post(KOMMO_WEBHOOK_URL, json=response_payload, timeout=15)
            end_time = time.time()
            print(f"⏳ Tempo de resposta do Kommo: {end_time - start_time:.2f} segundos")

            if response.status_code != 200:
                return jsonify({"error": "Erro ao enviar mensagem ao Kommo", "details": response.text}), 500
        except requests.Timeout:
            print("⏳ Timeout na requisição ao Kommo!")
            return jsonify({"error": "Kommo demorou para responder"}), 504
        except requests.RequestException as e:
            print(f"⚠️ Erro ao enviar ao Kommo: {e}")
            return jsonify({"error": "Erro ao enviar ao Kommo", "details": str(e)}), 500

        return jsonify({"reply": reply})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"🔥 ERRO DETECTADO 🔥\n{error_details}")
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Luiza está online e rodando!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
