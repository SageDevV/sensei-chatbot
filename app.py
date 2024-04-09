from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
from time import sleep
from helpers import *
from selecionar_persona import *
from selecionar_documento import *
from vision_havan import analisar_imagem
import uuid 

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-3.5-turbo"

app = Flask(__name__)
app.secret_key = 'alura'

caminho_imagem_enviada = None
caminho_arquivo_enviada = None

UPLOAD_FOLDER = 'dados' 

shipping_buffer = carrega('dados/shippingbuffer.txt')
contexto_dinamico = carrega('dados/contextodinamico.txt')

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

def bot(prompt):
    maximo_tentativas = 1
    repeticao = 0
    personalidade = selecionar_persona(prompt)
    contexto = selecionar_contexto(prompt)
    documento_selecionado = selecionar_documento(contexto)

    while True:
        try:
            prompt_do_sistema = f"""
            # Seu papel como assistente é oferecer uma experiência boa para o usuário que irá querer aprender sobre os processos da empresa Havan.

            # Você como assistente, deverá utilizar as informações que será fornecido via txt apenas. Não utilize a base de dados da internet para responder os usuários.
            # Você deve adotar a persona abaixo.
            
            # Contexto
            {documento_selecionado}
            
            # Persona
            {personalidade}
            """
            
            response = cliente.chat.completions.create(
                messages=[
                        {
                                "role": "system",
                                "content": prompt_do_sistema
                        },
                        {
                                "role": "user",
                                "content": prompt
                        }
                ],
                temperature=1,
                max_tokens=300,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model = "gpt-4-1106-preview")
            return response
        except Exception as erro:
                repeticao += 1
                if repeticao >= maximo_tentativas:
                        return "Erro no GPT: %s" % erro
                print('Erro de comunicação com OpenAI:', erro)
                sleep(1)
            


@app.route('/upload_arquivo', methods=['POST'])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']
        
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo

        return 'Imagem recebida com sucesso!', 200
    if 'arquivo' in request.files:
        arquivo_enviado = request.files['arquivo']
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(arquivo_enviado.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        arquivo_enviado.save(caminho_arquivo)
        dados_arquivo_atual = carrega(caminho_arquivo)
        contexto_dinamico = carrega("dados/contextodinamico.txt")
        contexto_dinamico = contexto_dinamico + '\n' + dados_arquivo_atual
        salva("dados/contextodinamico.txt", contexto_dinamico)
        os.remove(caminho_arquivo)
        restart_program()
    if 'audio' in request.files:
        return
    if 'video' in request.files:
        return
        
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
    
    prompt = request.json["msg"]
    resposta = bot(prompt)
    texto_resposta = resposta.choices[0].message.content
    return texto_resposta

@app.route("/transcricao")
def transcricao():
    return render_template("transcricao.html")

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
