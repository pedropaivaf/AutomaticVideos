import os
import sys
import glob
from src.roteirista import gerar_roteiro, gerar_metadados_youtube
from src.audio_engine import gerar_audio_dialogo
from src.transcritor import extrair_timestamps
from src.editor_visual import montar_video_splitscreen
from src.publicador import fazer_upload
from src.banco_dados import verificar_tema_existente, registrar_upload

def limpar_arquivos_temporarios():
    """Remove lixos de arquivos que podem ter ficado pela metade em caso de crash."""
    print("Executando limpeza de emergência...")
    for temp_file in glob.glob("temp_*.mp3"):
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Não foi possível remover o arquivo {temp_file}: {e}")
            
def iniciar_esteira():
    tema = "A farsa do sistema financeiro tradicional e a ilusão de trabalhar 8 horas por dia"
    print("="*50)
    print("🚀 INICIANDO ESTEIRA DO GERADOR DE SHORTS AUTÔNOMO 🚀")
    print(f"Tema: {tema}")
    print("="*50)
    
    # 0. Verificação de Memória (Supabase)
    print("\n[0/5] Checando Banco de Dados (Supabase)...")
    if verificar_tema_existente(tema):
        print("\033[91m[!] Tema já abordado no banco de dados. Encerrando operação para evitar redundância.\033[0m")
        sys.exit(0)
    
    try:
        # 1. Roteiro (LLM)
        print("\n[1/5] Acionando o Roteirista (OpenAI/LLM)...")
        json_roteiro = gerar_roteiro(tema, personagem1="Personagem1", personagem2="Personagem2", max_falas=6)
        if not json_roteiro:
            raise ValueError("O roteiro falhou ao ser gerado ou retornou vazio.")
            
        # 2. Áudio (ElevenLabs + Pydub)
        print("\n[2/5] Acionando o Diretor de Áudio (ElevenLabs + Pydub)...")
        audio_path = gerar_audio_dialogo(json_roteiro, personagem1="Personagem1", personagem2="Personagem2")
        
        # 3. Transcrição (Whisper)
        print("\n[3/5] Acionando o Transcritor (Whisper Word-Level)...")
        timestamps = extrair_timestamps(audio_path)
        if not timestamps:
            raise ValueError("A transcrição falhou ou não encontrou palavras.")
            
        # 4. Editor Visual (MoviePy) & Metadados
        print("\n[4/5] Gerando metadados de SEO para o YouTube...")
        metadados = gerar_metadados_youtube(tema)
        print(f"Título gerado: {metadados.get('titulo')}")
        
        print("\n[4.5/5] Acionando o Editor Visual (MoviePy)...")
        video_final = montar_video_splitscreen(audio_path, timestamps)
        
        # 5. Publicador (YouTube Data API)
        print("\n[5/5] Acionando o Publicador (Upload no YouTube)...")
        response_yt = fazer_upload(video_final, metadados)
        video_id = response_yt.get('id', 'ID_FALSO_DE_TESTE')
        
        # 6. Gravação do Estado
        print("\n[Registrando no Banco de Dados]...")
        registrar_upload(tema, metadados.get('titulo', ''), video_id)
        
        print("\n" + "="*50)
        print(f"🎉 SUCESSO ABSOLUTO! A esteira foi finalizada.")
        print(f"O vídeo foi renderizado em: {video_final}")
        print(f"Link do Shorts Privado: https://youtu.be/{video_id}")
        print("="*50)
        
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ ERRO CRÍTICO NA ESTEIRA: {e}")
        print("Interrompendo a execução de forma graciosa...")
        print("="*50)
        limpar_arquivos_temporarios()
        
if __name__ == "__main__":
    iniciar_esteira()
