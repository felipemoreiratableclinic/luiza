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
KOMMO_TOKEN = os.getenv("KOMMO_TOKEN")  # Token de longa duração do Kommo

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

def send_to_kommo(lead_id, message):
    """Envia a resposta para o Kommo de forma assíncrona"""
    try:
        response_payload = {
            "lead_id": lead_id,
            "message": message
        }
        print("🚀 Enviando resposta ao Kommo em segundo plano...")
        
        headers = {"Authorization": f"Bearer {KOMMO_TOKEN}"}  # Adicionando autenticação no envio
        response = requests.post(KOMMO_WEBHOOK_URL, json=response_payload, headers=headers, timeout=5)
        
        print(f"📤 Resposta do Kommo: {response.status_code}, {response.text}")
        
    except requests.Timeout:
        print("⏳ Timeout ao enviar ao Kommo! A mensagem pode não ter sido entregue.")
    except requests.RequestException as e:
        print(f"⚠️ Erro ao enviar ao Kommo: {e}")

@app.route("/kommo-webhook", methods=["POST"])
def kommo_webhook():
    """Rota que recebe mensagens do Kommo e responde via IA"""
    try:
        # Captura todos os cabeçalhos recebidos do Kommo
        headers_received = dict(request.headers)
        print(f"🔍 Todos os cabeçalhos recebidos: {headers_received}")  # Log de depuração

        # Captura os dados enviados pelo Kommo (agora como formulário)
        data = request.form.to_dict()  # Convertendo form-urlencoded para dicionário
        print(f"📩 Corpo da requisição recebida: {data}")

        # Captura o token se ele estiver no corpo da requisição
        auth_token = data.get("token")

        if auth_token:
            print(f"✅ Token encontrado no corpo da requisição: {auth_token}")
        else:
            print("❌ Nenhum Token foi enviado no corpo da requisição.")
            return jsonify({"error": "Unauthorized", "details": "Token ausente"}), 401

        # Verifica se o token enviado é válido
        if auth_token.strip() != KOMMO_TOKEN:
            print(f"❌ Token inválido! Recebido: {auth_token} | Esperado: {KOMMO_TOKEN}")
            return jsonify({"error": "Unauthorized", "details": "Token incorreto"}), 401

        user_message = data.get("message", "")
        lead_id = data.get("lead_id", "")

        if not user_message:
            return jsonify({"error": "Mensagem vazia recebida"}), 400

        # Gera resposta da IA
        reply = get_chatgpt_response(user_message)
        print(f"📝 Resposta da IA: {reply}")

        # Iniciar envio assíncrono ao Kommo
        threading.Thread(target=send_to_kommo, args=(lead_id, reply), daemon=True).start()

        # Responder imediatamente ao Kommo
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
