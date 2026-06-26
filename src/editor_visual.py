import os
import random
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip
)

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# AVISO CRÍTICO DE AMBIENTE:
# Para a geração de texto (TextClip) funcionar corretamente via MoviePy,
# é estritamente necessário ter o ImageMagick instalado na máquina.
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

def carregar_broll(duracao_audio: float) -> VideoFileClip:
    """
    Carrega um vídeo aleatório de gameplay/broll, redimensiona, corta para a duração 
    do áudio e posiciona na metade inferior.
    """
    broll_dir = os.path.join("assets", "broll")
    
    # Se a pasta não existir ou estiver vazia, geramos um fallback seguro
    if not os.path.exists(broll_dir):
        os.makedirs(broll_dir, exist_ok=True)
    arquivos = [f for f in os.listdir(broll_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
    
    if not arquivos:
        print("[AVISO] Nenhum vídeo encontrado em assets/broll/. Um erro será gerado se não houver arquivo.")
        raise FileNotFoundError("Adicione um vídeo de gameplay em assets/broll/ para renderizar.")
        
    broll_path = os.path.join(broll_dir, random.choice(arquivos))
    
    print(f"Carregando clipe B-Roll: {broll_path}")
    clip = VideoFileClip(broll_path)
    
    # Garantir que o broll é pelo menos tão longo quanto o áudio
    if clip.duration < duracao_audio:
        # Se for mais curto, idealmente faria um loop, mas para a v1 garantimos que pegue o que puder
        # Para ser robusto e exato ao pedido: "cortado para ter exatamente a mesma duração"
        clip = clip.fx(lambda c: c.loop(duration=duracao_audio))
    else:
        # Corta no tempo exato
        clip = clip.subclip(0, duracao_audio)
        
    # Crop central e resize para 1080x960 (Metade inferior)
    # A resolução padrão do clipe pode ser diferente. Redimensionamos e cortamos o centro.
    # Primeiro damos um resize de forma que a menor dimensão cubra (1080x960)
    # Em vez de resize e crop manuais pesados, usamos resize e margin/crop se necessário
    # Para simplificar e garantir 1080x960 exatos:
    clip = clip.resize(height=960)
    if clip.w < 1080:
        clip = clip.resize(width=1080)
    
    # Fazendo um crop central exato para 1080x960
    x_center = clip.w / 2
    y_center = clip.h / 2
    clip = clip.crop(x_center=x_center, y_center=y_center, width=1080, height=960)
    
    # Posiciona na metade inferior (y=960)
    clip = clip.set_position((0, 960))
    
    return clip

def montar_avatares(duracao_audio: float):
    """
    Carrega as imagens P1 e P2 e as posiciona lado a lado na metade superior.
    """
    p1_path = os.path.join("assets", "images", "p1.png")
    p2_path = os.path.join("assets", "images", "p2.png")
    
    if not os.path.exists(p1_path) or not os.path.exists(p2_path):
        raise FileNotFoundError("Avatares não encontrados! Verifique assets/images/p1.png e p2.png")
        
    # Cada avatar ocupará metade da largura (540) e a altura total superior (960)
    p1_clip = ImageClip(p1_path).resize(width=540, height=960).set_duration(duracao_audio).set_position((0, 0))
    p2_clip = ImageClip(p2_path).resize(width=540, height=960).set_duration(duracao_audio).set_position((540, 0))
    
    return [p1_clip, p2_clip]

def gerar_legendas(timestamps: list) -> list:
    """
    Gera TextClips cinéticos a partir do JSON de timestamps.
    """
    legendas = []
    
    for item in timestamps:
        palavra = item.get("palavra")
        inicio = item.get("inicio")
        fim = item.get("fim")
        
        # O TextClip precisa da fonte e estéticas fortes
        try:
            txt_clip = TextClip(
                palavra,
                fontsize=90,
                color='yellow',
                font='Impact',       # Impact ou Arial-Black
                stroke_color='black',
                stroke_width=5
            )
        except Exception as e:
            print(f"[AVISO] Falha ao carregar a fonte Impact, usando fallback nativo. Erro: {e}")
            txt_clip = TextClip(
                palavra,
                fontsize=90,
                color='yellow',
                stroke_color='black',
                stroke_width=5
            )
            
        txt_clip = txt_clip.set_start(inicio).set_end(fim)
        
        # Posicionamento exato no centro divisório das telas (x=center, y=960)
        # O MoviePy usa 'center' para x, centralizando a palavra horizontalmente.
        txt_clip = txt_clip.set_position(('center', 960))
        
        legendas.append(txt_clip)
        
    return legendas

def montar_video_splitscreen(audio_path: str, timestamps: list, output_path: str = None) -> str:
    """
    Orquestra todas as camadas e renderiza o vídeo final do Shorts/TikTok.
    """
    if output_path is None:
        output_dir = os.path.join("assets", "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "short_final.mp4")
        
    print(f"Iniciando montagem do Split-Screen. Carregando áudio: {audio_path}")
    audio_clip = AudioFileClip(audio_path)
    duracao_audio = audio_clip.duration
    
    print("Processando B-Roll (Metade Inferior)...")
    broll_clip = carregar_broll(duracao_audio)
    
    print("Processando Avatares Estáticos (Metade Superior)...")
    avatares = montar_avatares(duracao_audio)
    
    print("Processando Legendas Cinéticas (Centro)...")
    clips_legendas = gerar_legendas(timestamps)
    
    # Composição final
    # A resolução final do clipe CompositeVideoClip deve ser 1080x1920
    print("Empilhando camadas...")
    camadas = [broll_clip] + avatares + clips_legendas
    
    video_final = CompositeVideoClip(camadas, size=(1080, 1920))
    video_final = video_final.set_audio(audio_clip)
    
    # Exportação otimizada
    print(f"Renderizando vídeo final otimizado em {output_path}...")
    video_final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )
    
    print("Renderização concluída! Fechando recursos...")
    # Fechando recursos (prevenção de vazamento de memória)
    audio_clip.close()
    broll_clip.close()
    for avatar in avatares:
        avatar.close()
    for legenda in clips_legendas:
        legenda.close()
    video_final.close()
    
    return output_path


if __name__ == '__main__':
    # Bloco de Teste
    print("=== Iniciando Teste Local - Módulo 4 ===")
    
    from moviepy.editor import ColorClip
    from moviepy.audio.AudioClip import AudioArrayClip
    import numpy as np
    from PIL import Image
    
    # 1. Preparação de Mocks (Arquivos de teste)
    os.makedirs(os.path.join("assets", "broll"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images"), exist_ok=True)
    os.makedirs(os.path.join("assets", "outputs"), exist_ok=True)
    
    mock_broll_path = os.path.join("assets", "broll", "fake_gameplay.mp4")
    mock_p1_path = os.path.join("assets", "images", "p1.png")
    mock_p2_path = os.path.join("assets", "images", "p2.png")
    mock_audio_path = os.path.join("assets", "outputs", "dialogo_completo.mp3")
    
    print("Criando arquivos temporários de Mock para o teste visual...")
    
    # Cria avatares mock (imagens 540x960 com cor sólida para diferenciar)
    Image.new('RGB', (540, 960), color = (255, 0, 0)).save(mock_p1_path)  # Vermelho
    Image.new('RGB', (540, 960), color = (0, 0, 255)).save(mock_p2_path)  # Azul
    
    # Cria vídeo de broll mock de 3 segundos (cor verde) se não existir
    if not os.path.exists(mock_broll_path):
        ColorClip(size=(1080, 960), color=(0, 255, 0), duration=3).write_videofile(mock_broll_path, fps=10, logger=None)
        
    # Cria áudio mock de 3 segundos
    if not os.path.exists(mock_audio_path):
        # Tom puro para o áudio
        t = np.linspace(0, 3, 3 * 44100)
        audio_data = np.sin(2 * np.pi * 440 * t)
        audio_array = np.column_stack((audio_data, audio_data))
        AudioArrayClip(audio_array, fps=44100).write_audiofile(mock_audio_path, logger=None)
        
    # 2. Mock de Timestamps
    mock_timestamps = [
        {"palavra": "O", "inicio": 0.0, "fim": 0.5},
        {"palavra": "SISTEMA", "inicio": 0.6, "fim": 1.5},
        {"palavra": "FUNCIONA", "inicio": 1.6, "fim": 2.8}
    ]
    
    # 3. Execução
    try:
        resultado = montar_video_splitscreen(mock_audio_path, mock_timestamps)
        print(f"\\nTeste Concluído! O vídeo gerado deve estar em: {resultado}")
    except Exception as e:
        print(f"\\n=== FALHA NO TESTE ===\\n{e}")
        print("Lembrete: O ImageMagick está instalado e mapeado?")
