from openai import OpenAI
from dotenv import load_dotenv
import os
from helpers import encodar_imagem

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-vision-preview"

def analisar_imagem(caminho_imagem):
    prompt = """"
        Assuma que você é um assistente de chatbot e que provaelmente o usuário está enviado a foto de
        um produto. Faça uma análise dele
    """
    print(caminho_imagem)
    imagem_base64 = encodar_imagem(caminho_imagem)

    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text", "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{imagem_base64}",
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
    return resposta.choices[0].message.content

