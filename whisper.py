from io import BytesIO
import os
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
        

def transcrever_video(caminho_video):
    clip = mp.VideoFileClip(caminho_video)
    
    caminho_audio = "../dados/audio.mp3"
    clip.audio.write_audiofile(caminho_audio)
    transcrever_audio(caminho_audio)
    
    