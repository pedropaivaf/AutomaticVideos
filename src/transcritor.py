import os
import json
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Carregar variáveis de ambiente
load_dotenv()

# Setup do cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extrair_timestamps(audio_path: str) -> list:
    """
    Extrai as palavras e os tempos de um áudio utilizando a API Whisper da OpenAI.
    
    Args:
        audio_path (str): Caminho para o arquivo de áudio (.mp3)
        
    Returns:
        list: Lista de dicionários no formato [{"palavra": str, "inicio": float, "fim": float}]
    """
    if not os.path.exists(audio_path):
        print(f"[ERRO] Arquivo de áudio não encontrado: {audio_path}")
        return []

    try:
        print(f"Lendo arquivo de áudio: {audio_path}")
        with open(audio_path, "rb") as audio_file:
            print("Enviando áudio para a API Whisper da OpenAI...")
            
            # Chamada Mágica (Word-Level)
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            
            palavras_formatadas = []
            
            # Compatibilidade de extração (a resposta é um objeto dict-like ou Pydantic object dependendo da versão)
            words_data = getattr(response, 'words', [])
            if not words_data and isinstance(response, dict):
                words_data = response.get('words', [])
                
            for word_obj in words_data:
                # O formato do objeto word pode ser dict ou ter atributos
                if isinstance(word_obj, dict):
                    palavra = word_obj.get("word", "").strip()
                    inicio = word_obj.get("start", 0.0)
                    fim = word_obj.get("end", 0.0)
                else:
                    palavra = getattr(word_obj, "word", "").strip()
                    inicio = getattr(word_obj, "start", 0.0)
                    fim = getattr(word_obj, "end", 0.0)
                    
                palavras_formatadas.append({
                    "palavra": palavra,
                    "inicio": round(inicio, 2),
                    "fim": round(fim, 2)
                })
                
            print(f"Transcrição concluída com sucesso! Total de palavras capturadas: {len(palavras_formatadas)}")
            return palavras_formatadas
            
    except APIError as e:
        print(f"[ERRO CRÍTICO] Falha na API da OpenAI (Whisper): {e}")
        raise e
    except Exception as e:
        print(f"[ERRO INESPERADO] Falha durante a extração de timestamps: {e}")
        raise e

if __name__ == '__main__':
    # Teste de execução local do Módulo 3
    print("=== Iniciando Teste Local - Módulo 3 ===")
    teste_audio_path = os.path.join("assets", "outputs", "dialogo_completo.mp3")
    
    # Criar um arquivo dummy se não existir, já que o Módulo 2 usou uma API Key falsa
    # e não gerou o .mp3 real. Isso permitirá chegar na camada da OpenAI e testar o exception.
    if not os.path.exists(teste_audio_path):
        print(f"Aviso: {teste_audio_path} não encontrado.")
        print("Criando um arquivo MP3 falso apenas para acionar o erro de leitura da API Whisper...")
        os.makedirs(os.path.dirname(teste_audio_path), exist_ok=True)
        with open(teste_audio_path, "wb") as f:
            f.write(b"ID3... fake mp3 data")
            
    try:
        timestamps = extrair_timestamps(teste_audio_path)
        if timestamps:
            print("\nResultado da Transcrição (Primeiros 5 itens):")
            print(json.dumps(timestamps[:5], indent=2, ensure_ascii=False))
        else:
            print("Nenhum timestamp retornado pela API.")
    except Exception as e:
        print("\n=== FALHA ESPERADA NO TESTE (Chave OpenAI inválida / Arquivo de áudio falso) ===")
        print(f"Erro capturado: {e}")
        print("Certifique-se de configurar a OPENAI_API_KEY no .env para transcrever áudios reais.")
