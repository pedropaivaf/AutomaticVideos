import os
import importlib

# AVISO CRÍTICO DE AMBIENTE:
# Para a geração de texto (TextClip) funcionar corretamente via MoviePy,
# é estritamente necessário ter o ImageMagick instalado na máquina.
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

def montar_video_splitscreen(audio_path: str, timestamps: list, json_roteiro: list = None, output_path: str = None, nome_template: str = "podcast_split") -> str:
    """
    Roteador de templates visuais. Repassa os dados para o módulo correspondente em src/templates/.
    """
    try:
        print(f"Roteador visual acionado. Usando template: {nome_template}")
        modulo = importlib.import_module(f"src.templates.{nome_template}")
        resultado = modulo.render(audio_path, timestamps, json_roteiro, output_path)
        return resultado
    except ImportError as e:
        raise ValueError(f"Template '{nome_template}' não encontrado em src/templates/. Erro real: {e}")
    except Exception as e:
        print(f"Erro ao renderizar template '{nome_template}': {e}")
        raise e

if __name__ == '__main__':
    print("=== Iniciando Teste Local - Módulo Roteador de Templates ===")
    
    from moviepy.editor import ColorClip
    from moviepy.audio.AudioClip import AudioArrayClip
    import numpy as np
    from PIL import Image
    
    os.makedirs(os.path.join("assets", "broll"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images"), exist_ok=True)
    os.makedirs(os.path.join("assets", "outputs"), exist_ok=True)
    
    mock_broll_path = os.path.join("assets", "broll", "fake_gameplay.mp4")
    mock_p1_path = os.path.join("assets", "images", "p1.png")
    mock_p2_path = os.path.join("assets", "images", "p2.png")
    mock_audio_path = os.path.join("assets", "outputs", "dialogo_completo.mp3")
    
    print("Criando arquivos temporários de Mock para o teste visual...")
    Image.new('RGB', (540, 960), color = (255, 0, 0)).save(mock_p1_path)
    Image.new('RGB', (540, 960), color = (0, 0, 255)).save(mock_p2_path)
    
    if not os.path.exists(mock_broll_path):
        ColorClip(size=(1080, 960), color=(0, 255, 0), duration=3).write_videofile(mock_broll_path, fps=10, logger=None)
        
    if not os.path.exists(mock_audio_path):
        t = np.linspace(0, 3, 3 * 44100)
        audio_data = np.sin(2 * np.pi * 440 * t)
        audio_array = np.column_stack((audio_data, audio_data))
        AudioArrayClip(audio_array, fps=44100).write_audiofile(mock_audio_path, logger=None)
        
    mock_timestamps = [
        {"palavra": "O", "inicio": 0.0, "fim": 0.5},
        {"palavra": "SISTEMA", "inicio": 0.6, "fim": 1.5},
        {"palavra": "FUNCIONA", "inicio": 1.6, "fim": 2.8}
    ]
    
    try:
        resultado = montar_video_splitscreen(mock_audio_path, mock_timestamps, nome_template="cinematic_broll")
        print(f"\nTeste Concluído! O vídeo gerado deve estar em: {resultado}")
    except Exception as e:
        print(f"\n=== FALHA NO TESTE ===\n{e}")
