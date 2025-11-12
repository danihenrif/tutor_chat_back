import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import integration_service
import json
import requests 

load_dotenv()

client = openai.Client()

try:
    with open('initial_prompt.txt', 'r', encoding='utf-8') as arq :
        initial_prompt = arq.read()
except FileNotFoundError:
    print("ERRO: O arquivo 'initial_prompt.txt' não foi encontrado!")
    initial_prompt = "" 
    
global_student_data_cache = {} 
    
def geracao_texto(mensagens) :
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
        print(f"Erro na geração de texto: {e}")
        return jsonify({"erro": "Falha ao gerar resposta do bot."}), 500
    
@app.route('/receive-data', methods=['POST'])
def receive_data_from_professor():
    global global_student_data_cache
    
    try:
        dados = request.get_json()
        course_data = dados.get('course_data')
        progress_data = dados.get('progress_data')

        if not course_data or not progress_data:
            return jsonify({"status": "Dados faltando"}), 400

        json_final_string = integration_service.unify_and_send(course_data, progress_data)
        
        unificado = json.loads(json_final_string)
        student_id = unificado.get('student_id')
        
        if student_id:
            global_student_data_cache[student_id] = unificado
            return jsonify({"status": "Dados recebidos e processados com sucesso", "aluno_id": student_id}), 200
        else:
            return jsonify({"status": "ID do aluno faltando"}), 400

    except Exception as e:
        print(f"Erro no processamento de dados recebidos: {e}")
        return jsonify({"status": "Erro interno de processamento"}), 500
    
    
PROFESSOR_UPDATE_URL = "link da api do professor" 

@app.route('/update-progress', methods=['POST'])
def update_progress():
    try:
        progress_data = request.get_json()
        
        # 1. Envia o JSON recebido (progress_data) para a API do Professor Alan
        headers = {'Content-Type': 'application/json'} # AUTENTICAÇÃO ???
        
        response_alan = requests.post(
            PROFESSOR_UPDATE_URL, 
            json=progress_data, 
            headers=headers
        )
        
        # 2. Verifica a resposta do Professor Alan
        if response_alan.status_code == 200:
            # Sucesso: Os dados foram atualizados na Fonte de Verdade
            

            return jsonify({"status": "Progresso atualizado com sucesso no sistema do professor."}), 200
        else:
            #  Falha na API 
            return jsonify({
                "erro": "Falha ao atualizar progresso na API do professor.",
                "status_code_alan": response_alan.status_code
            }), 502 
            
    except Exception as e:
        print(f"Erro ao enviar progresso para o Professor Alan: {e}")
        return jsonify({"erro": "Erro de conexão ou processamento no backend."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)