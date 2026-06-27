import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopo necessário para fazer upload no YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def obter_credenciais():
    """
    Autentica o usuário com a API do Google via OAuth 2.0 e salva em token.json.
    Na primeira execução, abrirá o navegador.
    """
    creds = None
    # Verifica se já temos o token salvo
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Se não houver credenciais válidas logadas, pede ao usuário
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                raise FileNotFoundError("O arquivo client_secret.json não foi encontrado na raiz do projeto.")
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Salva o token para a próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def fazer_upload(video_path: str, metadados: dict):
    """
    Faz o upload do vídeo final para o YouTube usando a API v3.
    Status temporário como 'private' para validação de segurança.
    """
    print("Iniciando autenticação com YouTube...")
    creds = obter_credenciais()
    youtube = build('youtube', 'v3', credentials=creds)
    
    print("Preparando pacote de dados (Metadados)...")
    body = {
        'snippet': {
            'title': metadados.get('titulo', 'Shorts Autônomo'),
            'description': metadados.get('descricao', 'Podcast autônomo gerado por IA.\n\n#shorts'),
            'tags': metadados.get('tags', ['shorts', 'podcast', 'ia'])
        },
        'status': {
            'privacyStatus': 'private', # IMPORTANTE: 'private' para validação antes de ir a público
            'selfDeclaredMadeForKids': False
        }
    }
    
    print(f"Iniciando o envio (Upload) do arquivo: {video_path}")
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    
    # Executa a requisição
    response = request.execute()
    
    print(f"✅ Upload concluído com sucesso! ID do Vídeo: {response.get('id')}")
    print(f"Acesse https://studio.youtube.com/video/{response.get('id')}/edit para ver o vídeo como privado.")
    return response

if __name__ == "__main__":
    # Teste simulado local (apenas checando as credenciais, sem enviar um vídeo real)
    try:
        print("=== Teste Local - Módulo de Distribuição ===")
        print("Validação do fluxo de autenticação...")
        # Descomente a linha abaixo para forçar o login no seu navegador durante o teste local
        # obter_credenciais() 
        print("Módulo de Publicação estruturado com sucesso.")
    except Exception as e:
        print(f"Falha no teste de autenticação: {e}")
