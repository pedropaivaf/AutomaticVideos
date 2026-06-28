import os
import yt_dlp

def baixar_brolls():
    pastas_queries = {
        "minecraft": "ytsearch2:minecraft parkour gameplay no copyright vertical shorts",
        "gta": "ytsearch2:gta 5 mega ramp gameplay background no copyright vertical",
        "cinematic": "ytsearch2:luxury lifestyle money business b-roll no copyright vertical"
    }

    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "broll")

    for pasta, query in pastas_queries.items():
        dir_path = os.path.join(base_dir, pasta)
        os.makedirs(dir_path, exist_ok=True)
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(dir_path, 'video_%(autonumber)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False, # Showing some logs for feedback
        }
        
        print(f"Baixando 2 vídeos para a categoria '{pasta}'...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([query])
            except Exception as e:
                print(f"Erro ao baixar para a categoria {pasta}: {e}")
                
    print("Todos os B-Rolls foram populados com sucesso!")

if __name__ == "__main__":
    baixar_brolls()
