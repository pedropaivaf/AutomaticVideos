import os
import json
import whisper

def extrair_timestamps(audio_path: str) -> list:
    """
    Extrai as palavras e os tempos de um áudio utilizando o modelo Whisper local (base).
    
    Args:
        audio_path (str): Caminho para o arquivo de áudio (.mp3)
        
    Returns:
        list: Lista de dicionários no formato [{"palavra": str, "inicio": float, "fim": float}]
    """
    if not os.path.exists(audio_path):
        print(f"[ERRO] Arquivo de áudio não encontrado: {audio_path}")
        return []

    try:
        print(f"Lendo arquivo de áudio e carregando modelo Whisper local (base): {audio_path}")
        # Carrega o modelo whisper. Na primeira vez, ele fará o download do modelo base (~140MB).
        model = whisper.load_model("base")
        
        print("Transcrevendo áudio com word_timestamps=True...")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        palavras_formatadas = []
        
        segments = result.get("segments", [])
        for segment in segments:
            words = segment.get("words", [])
            for w in words:
                palavra = w.get("word", "").strip()
                inicio = w.get("start", 0.0)
                fim = w.get("end", 0.0)
                
                if palavra:
                    palavras_formatadas.append({
                        "palavra": palavra,
                        "inicio": round(inicio, 2),
                        "fim": round(fim, 2)
                    })
                    
        print(f"Transcrição concluída com sucesso! Total de palavras capturadas: {len(palavras_formatadas)}")
        return palavras_formatadas
        
    except Exception as e:
        print(f"[ERRO INESPERADO] Falha durante a extração de timestamps com Whisper local: {e}")
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
