import os
import assemblyai as aai
import moviepy.editor as mp

def transcrever_audio(caminho_audio):
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(caminho_audio)

    if transcript.status == aai.TranscriptStatus.error:
        print(transcript.error)
    else:
        print(transcript.text)
        

def transcrever_video(caminho_video):
    clip = mp.VideoFileClip(caminho_video)
    
    caminho_audio = "../dados/audio.mp3"
    clip.audio.write_audiofile(caminho_audio)
    transcrever_audio(caminho_audio)
    
    