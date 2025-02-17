import os
import time
import threading
from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Pegando as variáveis de ambiente do Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KOMMO_WEBHOOK_URL = os.getenv("KOMMO_WEBHOOK_URL")
KOMMO_TOKEN = os.getenv("KOMMO_TOKEN")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_chatgpt_response(message):
    """Gera uma resposta da IA para o lead"""
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

def send_to_kommo(chat_id, contact_id, talk_id, message):
    """Envia a resposta ao Kommo"""
    try:
        response_payload = {
            "message": {
                "chat_id": chat_id,
                "contact_id": contact_id,
                "talk_id": talk_id,
                "text": message,
                "type": "outgoing"
            }
        }

        headers = {
            "Authorization": f"Bearer {KOMMO_TOKEN}",
            "Content-Type": "application/json"
        }

        print("🚀 Enviando resposta ao Kommo...")
        response = requests.post(KOMMO_WEBHOOK_URL, json=response_payload, headers=headers, timeout=5)

        if response.status_code == 200:
            print(f"✅ Resposta enviada ao Kommo com sucesso: {response.text}")
        else:
            print(f"⚠️ Erro ao enviar resposta ao Kommo! Código: {response.status_code}, Resposta: {response.text}")

    except requests.Timeout:
        print("⏳ Timeout ao enviar ao Kommo! A mensagem pode não ter sido entregue.")
    except requests.RequestException as e:
        print(f"⚠️ Erro ao enviar ao Kommo: {e}")

@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    """Rota que recebe mensagens do Kommo e responde via IA"""
    try:
        headers_received = dict(request.headers)
        print(f"🔍 Todos os cabeçalhos recebidos: {headers_received}")

        data = request.form.to_dict()
        print(f"📩 Corpo da requisição recebida: {data}")

        # Captura os IDs necessários
        chat_id = data.get("message[add][0][chat_id]", "")
        contact_id = data.get("message[add][0][contact_id]", "")
        talk_id = data.get("message[add][0][talk_id]", "")
        user_message = data.get("message[add][0][text]", "")

        if not user_message:
            return jsonify({"error": "Mensagem vazia recebida"}), 400

        # Gera resposta da IA
        reply = get_chatgpt_response(user_message)
        print(f"📝 Resposta da IA: {reply}")

        # Enviar ao Kommo
        threading.Thread(target=send_to_kommo, args=(chat_id, contact_id, talk_id, reply), daemon=True).start()

        return jsonify({"reply": reply})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"🔥 ERRO DETECTADO 🔥\n{error_details}")
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    """Verifica se a API está rodando"""
    return jsonify({"status": "Luiza está online e rodando!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
