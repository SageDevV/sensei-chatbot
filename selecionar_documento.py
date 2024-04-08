from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4"

shipping_buffer = carrega('dados/shippingbuffer.txt')

def selecionar_documento(resposta_openai):
    if "shippingbuffer" in resposta_openai:
        return shipping_buffer
    else:
        return shipping_buffer 

def selecionar_contexto(mensagem_usuario):
    prompt_sistema = f"""
    A empresa Havan contém diversos contextos

    #Documento 2 "\n" {shipping_buffer} "\n"

    Avalie o prompt do usuário e retorne o documento mais indicado para ser usado no contexto da resposta. Retorne dados se for o Documento 1, políticas se for o Documento 2 e produtos se for o Documento 3. 

    """

    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content" : mensagem_usuario
            }
        ],
        temperature=1,
    )

    contexto = resposta.choices[0].message.content.lower()

    return contexto