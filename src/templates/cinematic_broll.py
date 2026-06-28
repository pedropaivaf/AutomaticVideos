import os
import random
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    ColorClip
)

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def carregar_broll_full(duracao_audio: float, tema_broll: str = "cinematic") -> VideoFileClip:
    """Carrega b-roll, faz crop para 1080x1920 (tela cheia) e corta tempo."""
    broll_dir = os.path.join("assets", "broll", tema_broll)
    if not os.path.exists(broll_dir):
        os.makedirs(broll_dir, exist_ok=True)
    arquivos = [f for f in os.listdir(broll_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
    
    if not arquivos:
        # Fallback to general broll folder if empty
        broll_dir = os.path.join("assets", "broll")
        arquivos = [f for f in os.listdir(broll_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
        if not arquivos:
            print("[AVISO] Nenhum vídeo encontrado em assets/broll/. Um erro será gerado se não houver arquivo.")
            raise FileNotFoundError("Adicione um vídeo de gameplay/cinematic em assets/broll/ para renderizar.")
        
    broll_path = os.path.join(broll_dir, random.choice(arquivos))
    clip = VideoFileClip(broll_path)
    
    if clip.duration < duracao_audio:
        clip = clip.fx(lambda c: c.loop(duration=duracao_audio))
    else:
        clip = clip.subclip(0, duracao_audio)
        
    # Crop central exato para 1080x1920
    clip = clip.resize(height=1920)
    if clip.w < 1080:
        clip = clip.resize(width=1080)
    
    x_center = clip.w / 2
    y_center = clip.h / 2
    clip = clip.crop(x_center=x_center, y_center=y_center, width=1080, height=1920)
    clip = clip.set_position((0, 0))
    
    return clip

def gerar_legendas(timestamps: list, cor_legenda: str = 'yellow') -> list:
    legendas = []
    for item in timestamps:
        palavra = item.get("palavra")
        inicio = item.get("inicio")
        fim = item.get("fim")
        
        try:
            txt_clip = TextClip(
                palavra,
                fontsize=110,
                color=cor_legenda,
                font='Arial-Black',
                stroke_color='black',
                stroke_width=3
            )
        except Exception:
            txt_clip = TextClip(
                palavra,
                fontsize=110,
                color=cor_legenda,
                stroke_color='black',
                stroke_width=3
            )
            
        txt_clip = txt_clip.set_start(inicio).set_end(fim)
        txt_clip = txt_clip.set_position(('center', 'center'))
        legendas.append(txt_clip)
        
    return legendas

def render(audio_path: str, timestamps: list, json_roteiro: list = None, output_path: str = None, tema_broll: str = "cinematic", cor_legenda: str = "yellow", is_landing_page: bool = False) -> str:
    if output_path is None:
        output_dir = os.path.join("assets", "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "short_final.mp4")
        
    audio_clip = AudioFileClip(audio_path)
    duracao_audio = audio_clip.duration
    
    broll_clip = carregar_broll_full(duracao_audio, tema_broll)
    
    # Overlay escuro para destacar texto (-30% / 0.3 opacity for Landing Pages, else 0.15)
    opacity = 0.3 if is_landing_page else 0.15
    overlay_escuro = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_opacity(opacity).set_duration(duracao_audio).set_position((0, 0))
    
    clips_legendas = gerar_legendas(timestamps, cor_legenda)
    
    camadas = [broll_clip, overlay_escuro] + clips_legendas
    video_final = CompositeVideoClip(camadas, size=(1080, 1920))
    video_final = video_final.set_audio(audio_clip)
    
    video_final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )
    
    audio_clip.close()
    broll_clip.close()
    overlay_escuro.close()
    for legenda in clips_legendas:
        legenda.close()
    video_final.close()
    
    return output_path
