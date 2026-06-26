import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Carregar variáveis de ambiente
load_dotenv()

# Setup de Vozes (Placeholders para ElevenLabs)
# Substituir pelos IDs reais das vozes desejadas
VOICE_ID_P1 = "pNInz6obbfDQGcgMyIGb" # Ex: Adam (Padrão)
VOICE_ID_P2 = "ErXwobaYiN019PkySvjV" # Ex: Antoni (Padrão)

def gerar_audio_dialogo(json_roteiro: list, personagem1: str = "Personagem1", personagem2: str = "Personagem2") -> str:
    """
    Gera o áudio multi-voz de um diálogo, remove silêncios para retenção e salva o arquivo final.
    
    Args:
        json_roteiro (list): Roteiro gerado pelo Módulo 1.
        personagem1 (str): Nome do personagem 1 (para mapear a voz).
        personagem2 (str): Nome do personagem 2 (para mapear a voz).
        
    Returns:
        str: Caminho do arquivo de áudio final gerado.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "sua_chave_aqui":
        print("AVISO: ELEVENLABS_API_KEY não configurada. Certifique-se de adicionar no .env")
        # Dependendo de como a lib se comporta, ela pode pegar de variaveis de ambiente
        # mas vamos inicializar o cliente explicitamente.

    client = ElevenLabs(api_key=api_key)
    
    arquivos_temporarios = []
    
    # Geração Dinâmica
    for i, linha in enumerate(json_roteiro):
        personagem_atual = linha.get("personagem")
        texto = linha.get("texto")
        
        # Mapeamento de vozes
        voice_id = VOICE_ID_P1 if personagem_atual == personagem1 else VOICE_ID_P2
        
        temp_filename = f"temp_{i}.mp3"
        print(f"Gerando áudio para {personagem_atual} ({i+1}/{len(json_roteiro)})...")
        
        try:
            # Requisitando o áudio via ElevenLabs
            audio_generator = client.text_to_speech.convert(
                voice_id=voice_id,
                text=texto,
                model_id="eleven_multilingual_v2"
            )
            
            # Salvando o arquivo temporário
            with open(temp_filename, "wb") as f:
                for chunk in audio_generator:
                    if chunk:
                        f.write(chunk)
                        
            arquivos_temporarios.append(temp_filename)
            
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao gerar áudio com ElevenLabs na linha {i}: {texto}")
            print(f"Detalhes do erro: {str(e)}")
            # Limpar arquivos temporários antes de lançar a exceção
            for temp_file in arquivos_temporarios:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            raise e
            
    print("Todos os áudios gerados. Iniciando orquestração com Pydub...")
    
    # Orquestração com Pydub
    audio_completo = AudioSegment.empty()
    for temp_file in arquivos_temporarios:
        segmento = AudioSegment.from_mp3(temp_file)
        audio_completo += segmento
        
    # O Hack da Retenção (Remoção de Silêncios)
    print("Aplicando hack de retenção (removendo pausas > 200ms)...")
    chunks_sem_silencio = split_on_silence(
        audio_completo,
        min_silence_len=200,      # Corta qualquer pausa maior que 200ms
        silence_thresh=-40,       # Limite de dB que é considerado silêncio
        keep_silence=50           # Mantém um micro silêncio (50ms) pra não ficar robótico demais
    )
    
    audio_otimizado = AudioSegment.empty()
    for chunk in chunks_sem_silencio:
        audio_otimizado += chunk
        
    # Exportação
    output_dir = os.path.join("assets", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    caminho_final = os.path.join(output_dir, "dialogo_completo.mp3")
    
    print(f"Exportando áudio final para: {caminho_final}")
    audio_otimizado.export(caminho_final, format="mp3")
    
    # Limpeza dos arquivos temporários
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
