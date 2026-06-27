import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def obter_cliente() -> Client:
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_KEY", "")
    
    if not url or not key:
        print("[AVISO] SUPABASE_URL ou SUPABASE_KEY ausentes no .env.")
        
    return create_client(url, key)

def verificar_tema_existente(tema: str) -> bool:
    """
    Verifica se o tema já foi processado anteriormente.
    Retorna True se existir, False caso contrário.
    """
    try:
        supabase = obter_cliente()
        response = supabase.table("historico_shorts").select("id").eq("tema_original", tema).execute()
        
        # Se o array de dados não estiver vazio, o tema já existe
        if len(response.data) > 0:
            return True
        return False
    except Exception as e:
        print(f"[ERRO - Banco de Dados] Falha na verificação do tema: {e}")
        # Se falhar a conexão, vamos assumir False para não travar a esteira indevidamente.
        # Pode ser alterado se preferir bloquear.
        return False

def registrar_upload(tema: str, titulo: str, video_id: str):
    """
    Registra os metadados do vídeo que foi enviado no banco de dados.
    """
    try:
        supabase = obter_cliente()
        data = {
            "tema_original": tema,
            "titulo_gerado": titulo,
            "youtube_video_id": video_id
        }
        # Inserção no banco
        response = supabase.table("historico_shorts").insert(data).execute()
        print(f"✅ [Supabase] Histórico registrado com sucesso! Tema salvo: {tema}")
        return True
    except Exception as e:
        print(f"[ERRO CRÍTICO - Banco de Dados] Não foi possível salvar o estado no Supabase: {e}")
        return False
        
if __name__ == "__main__":
    # Teste de execução local com mocks
    print("=== Teste Local - Módulo de Memória ===")
    mock_tema = "A farsa do sistema financeiro tradicional e a ilusão de trabalhar 8 horas por dia"
    
    print("Testando verificação de tema...")
    existe = verificar_tema_existente(mock_tema)
    print(f"O tema existe no banco? {existe}")
    
    print("\nTestando registro de upload...")
    # registrar_upload(mock_tema, "Título Mock", "mock_video_123")
    print("Teste concluído. (Descomente o comando de insert para realizar um registro de fato)")
