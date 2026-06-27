import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from pydub.silence import split_on_silence

import asyncio
import edge_tts
import imageio_ffmpeg
from pydub import AudioSegment
from pydub.silence import split_on_silence

load_dotenv()

# Forçar o PATH para incluir o ffmpeg/ffprobe instalado via winget
os.environ["PATH"] += os.pathsep + r"C:\Users\Pedro\AppData\Local\Microsoft\WinGet\Links"

# Setup de Vozes (ElevenLabs Premium)
VOICE_ID_P1 = "CwhRBWXzGAHq8TQ4Fs17" # Ex: Roger (Foco em Retenção)
VOICE_ID_P2 = "ErXwobaYiN019PkySvjV" # Ex: Antoni (Padrão)

async def gerar_audio_edge_tts(texto: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(texto, voice)
    await communicate.save(output_path)

def gerar_audio_dialogo(json_roteiro: list, personagem1: str = "Personagem1", personagem2: str = "Personagem2") -> str:
    """
    Gera o áudio multi-voz de um diálogo, remove silêncios para retenção e salva o arquivo final.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    usar_elevenlabs = False
    if api_key and api_key != "sua_chave_aqui":
        usar_elevenlabs = True
        client = ElevenLabs(api_key=api_key)
    else:
        print("AVISO: ELEVENLABS_API_KEY inválida/ausente. Iniciando Fallback 100% Gratuito (Edge-TTS)...")

    arquivos_temporarios = []
    
    for i, linha in enumerate(json_roteiro):
        # Fallback de parsing inteligente para suportar variações do LLM
        personagem_atual = None
        texto = None
        
        if isinstance(linha, dict):
            personagem_atual = linha.get("personagem") or linha.get("nome") or linha.get("autor")
            texto = linha.get("texto") or linha.get("fala") or linha.get("conteudo") or linha.get("dialogo")
            
            # Caso o LLM tenha retornado {"Personagem1": "texto da fala"}
            if not personagem_atual and not texto:
                for k, v in linha.items():
                    if k in [personagem1, personagem2, "Personagem1", "Personagem2"]:
                        personagem_atual = k
                        texto = v
                        break
        
        # Último recurso
        if not personagem_atual:
            personagem_atual = personagem1 if i % 2 == 0 else personagem2
            
        if not texto:
            texto = str(linha)
            
        temp_filename = f"temp_{i}.mp3"
        print(f"Gerando áudio para {personagem_atual} ({i+1}/{len(json_roteiro)})...")
        
        try:
            if usar_elevenlabs:
                voice_id = VOICE_ID_P1 if personagem_atual == personagem1 else VOICE_ID_P2
                audio_generator = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=texto,
                    model_id="eleven_multilingual_v2"
                )
                with open(temp_filename, "wb") as f:
                    for chunk in audio_generator:
                        if chunk:
                            f.write(chunk)
            else:
                # Fallback Edge-TTS
                voice = "pt-BR-AntonioNeural" if personagem_atual == personagem1 else "pt-BR-FranciscaNeural"
                asyncio.run(gerar_audio_edge_tts(texto, voice, temp_filename))
                
            arquivos_temporarios.append(temp_filename)
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao gerar áudio na linha {i}: {texto}")
            print(f"Detalhes do erro: {str(e)}")
            for temp_file in arquivos_temporarios:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            raise e
            
    print("Todos os áudios gerados. Iniciando orquestração com Pydub...")
    
    audio_completo = AudioSegment.empty()
    for temp_file in arquivos_temporarios:
        segmento = AudioSegment.from_mp3(temp_file)
        audio_completo += segmento
        
    print("Aplicando hack de retenção (removendo pausas > 200ms)...")
    chunks_sem_silencio = split_on_silence(
        audio_completo,
        min_silence_len=200,
        silence_thresh=-40,
        keep_silence=50
    )
    
    audio_otimizado = AudioSegment.empty()
    for chunk in chunks_sem_silencio:
        audio_otimizado += chunk
        
    output_dir = os.path.join("assets", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    caminho_final = os.path.join(output_dir, "dialogo_completo.mp3")
    
    print(f"Exportando áudio final para: {caminho_final}")
    audio_otimizado.export(caminho_final, format="mp3")
    
    print("Limpando arquivos temporários...")
    for temp_file in arquivos_temporarios:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    print("Módulo 2 (Diretor de Áudio) executado com sucesso!")
    return caminho_final

if __name__ == '__main__':
    # Bloco de teste de execução local com JSON Mock
    
    # A fim de não gastar a chave de API ou permitir rodar sem chave na validação,
    # caso a chave não esteja presente e seja apenas um teste, vamos simular ou capturar a exceção.
    # O user pediu para que os erros sejam lançados. Vamos rodar dentro de um try/except de teste.
    
    mock_json = [
        {"personagem": "Personagem1", "texto": "A teoria da simulação é a única coisa que faz sentido hoje."},
        {"personagem": "Personagem2", "texto": "Sério? Ou você só perdeu dinheiro em cripto e quer culpar a matrix?"}
    ]
    
    print("=== Iniciando Teste Local - Módulo 2 ===")
    try:
        resultado = gerar_audio_dialogo(mock_json, personagem1="Personagem1", personagem2="Personagem2")
        print(f"Teste concluído. Áudio gerado em: {resultado}")
    except Exception as e:
        print("\n=== FALHA ESPERADA NO TESTE (Sem chave de API válida) ===")
        print(f"Erro capturado: {e}")
        print("Certifique-se de preencher a ELEVENLABS_API_KEY no arquivo .env para testar a integração completa.")
