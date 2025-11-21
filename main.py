import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests 

load_dotenv()

APITUTOR_URL = os.getenv("APITUTOR_BASE_URL", "http://localhost:3000/api")
COURSE_ID = os.getenv("COURSE_ID", "edb-01")

client = openai.Client()

try:
    with open('initial_prompt.txt', 'r', encoding='utf-8') as arq :
        initial_prompt = arq.read()
except FileNotFoundError:
    print("ERRO: O arquivo 'initial_prompt.txt' não foi encontrado!")
    initial_prompt = "" 

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        temperature=0,
        max_tokens=1000,
        stream=True
    )
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            texto_completo += texto  
    return texto_completo

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.get_json()
    pergunta_usuario = dados.get('pergunta')
    historico_mensagens = dados.get('mensagens', [])
    
    if not pergunta_usuario:
        return jsonify({"erro": "Nenhuma pergunta fornecida"}), 400

    if not historico_mensagens and initial_prompt:
        historico_mensagens.append({"role": "system", "content": initial_prompt})
        
    historico_mensagens.append({"role": "user", "content": pergunta_usuario})
    
    try:
        resposta_bot_texto = geracao_texto(historico_mensagens)
        historico_mensagens.append({"role" : "assistant", "content" : resposta_bot_texto})
        
        return jsonify({
            "resposta": resposta_bot_texto,
            "historico_atualizado": historico_mensagens
        })
    
    except Exception as e:
        return jsonify({"erro": "Falha ao gerar resposta do bot."}), 500

@app.route('/get-viewed-lessons/<string:student_id>', methods=['GET'])
def get_viewed_lessons(student_id):
    try:
        url = f"{APITUTOR_URL}/course/{COURSE_ID}/student/{student_id}/lessons/viewed"
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/update-progress/<string:student_id>', methods=['POST'])
def update_progress(student_id):
    try:
        dados = request.get_json()
        
        url = f"{APITUTOR_URL}/course/{COURSE_ID}/student/{student_id}/progress"
        
        payload_apitutor = {
            "lesson_id": dados.get('lesson_id'),
            "status": dados.get('status')
        }
        
        response = requests.post(url, json=payload_apitutor)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/student-data/<string:student_id>', methods=['GET'])
def get_course_data(student_id):
    try:
        url = f"{APITUTOR_URL}/course/{COURSE_ID}/student/{student_id}"
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/register-student', methods=['POST'])
def register_student():
    try:
        dados = request.get_json()
        url = f"{APITUTOR_URL}/student"
        response = requests.post(url, json=dados)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)