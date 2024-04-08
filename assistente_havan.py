from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
import json

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"
contexto = carrega("dados/ecomart.txt")

def criar_lista_ids():
    lista_ids_arquivos = []

    file_dados = cliente.files.create(
        file=open("dados/dados_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_dados.id)

    file_politicas = cliente.files.create(
        file=open("dados/políticas_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_politicas.id)

    file_produtos = cliente.files.create(
        file=open("dados/produtos_ecomart.txt","rb"),
        purpose="assistants"
    )

    lista_ids_arquivos.append(file_produtos.id)

    return lista_ids_arquivos

def pegar_json():
    filename = "assistentes.json"
    
    if not os.path.exists(filename):
        thread_id = criar_thread()
        file_id_list = criar_lista_ids()
        assistant_id = criar_assistente(file_id_list)
        data = {
            "assistant_id": assistant_id.id,
            "thread_id": thread_id.id,
            "file_ids": file_id_list
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Arquivo 'assistentes.json' criado com sucesso.")
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Arquivo 'assistentes.json' não encontrado.")


def criar_thread():
    return cliente.beta.threads.create()

def criar_assistente(file_ids=[]):
    assistente = cliente.beta.assistants.create(
        name="Sensei",
        instructions = 
        f"""
            # Seu papel como assistente é oferecer uma experiência boa para o usuário que irá querer aprender sobre os processos da empresa Havan.

            # FAQ:

            Q: Quem é você?
            A: Meu nome é Sensei e serei seu assistente para auxiliar em suas dúvidas quanto aos processos da Havan.

            Q: Qual é seu objetivo?
            A: Oferecer a melhor experiência para todos os funcionários da Havan quantos aos processos e produtos da mesma.

            Q: Quais são as áreas de foco da Havan?
            A: Logística, Financeiro, Contabilidade, Fiscal, Marketing e PDV

            Q: Qual é a base de dados mais consumida da Havan?
            A: Base de dados Itlsys. SGBD Sql server
        """,
        model = modelo,
        file_ids = file_ids,
        tools=[{"type": "code_interpreter"},{"type": "retrieval"}]
    )
    return assistente

