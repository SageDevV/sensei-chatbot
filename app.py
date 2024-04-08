from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
from selecionar_documento import *
from assistente_havan import *
from vision_havan import analisar_imagem
import uuid 

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"

app = Flask(__name__)
app.secret_key = 'alura'

assistente = pegar_json()
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

STATUS_COMPLETED = "completed" 
STATUS_REQUIRES_ACTION = "requires_action" 

caminho_imagem_enviada = None
UPLOAD_FOLDER = 'dados' 

def bot(prompt):
    global caminho_imagem_enviada
    maximo_tentativas = 1
    repeticao = 0

    while True:
        try:
            personalidade = personas[selecionar_persona(prompt)]

            cliente.beta.threads.messages.create(
                thread_id=thread_id, 
                role = "user",
                content =  f"""
                
                Assuma, de agora em diante, a personalidade abaixo. 
                Ignore as personalidades anteriores.

                # Persona
                {personalidade}
                """,
                file_ids=file_ids
            )

            run = cliente.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistente_id
            )

            while run.status != STATUS_COMPLETED:
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
            )
            
            historico = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
            resposta = historico[0]
            return resposta

        except Exception as erro:
                repeticao += 1
                if repeticao >= maximo_tentativas:
                        return "Erro no GPT: %s" % erro
                print('Erro de comunicação com OpenAI:', erro)
                sleep(1)
            


@app.route('/upload_imagem', methods=['POST'])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']
        
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo

        return 'Imagem recebida com sucesso!', 200
    return 'Nenhum arquivo foi enviado', 400

@app.route("/chat", methods=["POST"])
def chat():
    global caminho_imagem_enviada
    prompt = request.json["msg"]
    
    resposta_vision = ""            
    if caminho_imagem_enviada != None:
        resposta_vision = analisar_imagem(caminho_imagem_enviada)
        os.remove(caminho_imagem_enviada)
        caminho_imagem_enviada = None
        return resposta_vision
    
    resposta = bot(prompt)
    print(resposta)
    if hasattr(resposta, 'content') and resposta.content:
        texto_resposta = resposta.content[0].text.value
    else:
        texto_resposta = None
        
    return texto_resposta

@app.route("/transcricao")
def transcricao():
    return render_template("transcricao.html")

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
