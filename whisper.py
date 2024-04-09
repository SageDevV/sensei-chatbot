import os
from time import sleep
from helpers import carrega, salva
from openai import OpenAI
import moviepy.editor as mp

def transcrever_audio(caminho_audio):
    cliente = OpenAI()
    cliente.api_key = os.getenv("OPENAI_API_KEY")
    
    with open(caminho_audio, 'rb') as audio_file:
        transcription = cliente.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )

    print(transcription)
    os.remove(caminho_audio)
    return transcription
        

def transcrever_video(caminho_video):
    clip = mp.VideoFileClip(caminho_video)
    
    caminho_audio = "../dados/audio.mp3"
    clip.audio.write_audiofile(caminho_audio)
    transcrever_audio(caminho_audio)
    
def gravar_contexto_dinamico(transcription):
    cliente = OpenAI()
    cliente.api_key = os.getenv("OPENAI_API_KEY")
    maximo_tentativas = 1
    repeticao = 0
    try:
        prompt_do_sistema = f"""
        # Seu papel como assistente é utilizar a transcrição que o usuário irá fornecer para criar um sistema de perguntas e respostas
        
        # Utilize esse formato de saída para criar um sistema de perguntas e respostas
        Q1: Quantos anos de história a Havan tem? 
        A1: A Havan tem 37 anos de história.
        
        """
        
        response = cliente.chat.completions.create(
            messages=[
                    {
                            "role": "system",
                            "content": prompt_do_sistema
                    },
                    {
                            "role": "user",
                            "content": transcription
                    }
            ],
            temperature=1,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            model = "gpt-4-1106-preview")
        
        print(response.choices[0].message.content)

        contexto_dinamico = carrega("dados/contextodinamico.txt")
        contexto_dinamico = contexto_dinamico + '\n' + response.choices[0].message.content
        salva("dados/contextodinamico.txt", contexto_dinamico)
    except Exception as erro:
            repeticao += 1
            if repeticao >= maximo_tentativas:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)
            

    
    