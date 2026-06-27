import os
import sys
import glob

from src.roteirista import gerar_roteiro, gerar_roteiro_de_url, escolher_template, gerar_metadados_youtube
from src.audio_engine import gerar_audio_dialogo
from src.transcritor import extrair_timestamps
from src.editor_visual import montar_video_splitscreen
from src.publicador import fazer_upload
from src.banco_dados import verificar_tema_existente, registrar_upload
from src.extrator_url import raspar_landing_page

def limpar_arquivos_temporarios():
    """Remove lixos de arquivos que podem ter ficado pela metade em caso de crash."""
    print("Executando limpeza de emergência...")
    for temp_file in glob.glob("temp_*.mp3"):
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Não foi possível remover o arquivo {temp_file}: {e}")
            
def iniciar_esteira(input_str: str):
    """
    Inicia a esteira de vídeos. Recebe um tema textual ou uma URL (Landing Page).
    """
    print("="*50)
    print("🚀 INICIANDO ESTEIRA DO GERADOR DE SHORTS AUTÔNOMO V3 🚀")
    print(f"Input: {input_str}")
    print("="*50)
    
    is_url = input_str.startswith("http://") or input_str.startswith("https://")
    
    try:
        if is_url:
            print("\n[Fluxo URL-to-Short Ativado]")
            
            # 0. Verificação de Memória (Supabase) baseada na URL
            print("\n[0/5] Checando Banco de Dados (Supabase) para a URL...")
            if verificar_tema_existente(input_str):
                print("\033[91m[!] URL já processada no banco de dados. Encerrando operação para evitar redundância.\033[0m")
                sys.exit(0)
                
            # 1. Extrator e Roteiro de URL
            print("\n[1/5] Extraindo conteúdo da URL...")
            texto_raspado = raspar_landing_page(input_str)
            if not texto_raspado:
                raise ValueError("A raspagem da URL falhou ou não retornou texto.")
                
            print("\n[1.5/5] Acionando o Roteirista (Copywriter de Resposta Direta)...")
            json_roteiro = gerar_roteiro_de_url(texto_raspado)
            if not json_roteiro:
                raise ValueError("O roteiro de URL falhou ao ser gerado ou retornou vazio.")
                
            nome_template = "cinematic_broll"
            
            # 2. Áudio
            print("\n[2/5] Acionando o Diretor de Áudio (ElevenLabs)...")
            # Como o narrador da URL usa o nome "Narrador", usaremos esse nome na engine
            audio_path = gerar_audio_dialogo(json_roteiro, personagem1="Narrador", personagem2="None")
            
            # Para metadados
            tema_ou_url = input_str
            url_origem = input_str
            
        else:
            print("\n[Fluxo Tema Dinâmico Ativado]")
            
            # 0. Verificação de Memória (Supabase)
            print("\n[0/5] Checando Banco de Dados (Supabase)...")
            if verificar_tema_existente(input_str):
                print("\033[91m[!] Tema já abordado no banco de dados. Encerrando operação para evitar redundância.\033[0m")
                sys.exit(0)
                
            # 1. Roteiro Padrão
            print("\n[1/5] Acionando o Roteirista e escolhendo Template...")
            nome_template = escolher_template(input_str)
            print(f"-> A IA escolheu o template visual: {nome_template}")
            
            json_roteiro = gerar_roteiro(input_str, personagem1="Personagem1", personagem2="Personagem2", max_falas=6)
            if not json_roteiro:
                raise ValueError("O roteiro falhou ao ser gerado ou retornou vazio.")
                
            # 2. Áudio
            print("\n[2/5] Acionando o Diretor de Áudio (ElevenLabs + Pydub)...")
            audio_path = gerar_audio_dialogo(json_roteiro, personagem1="Personagem1", personagem2="Personagem2")
            
            tema_ou_url = input_str
            url_origem = None

        # 3. Transcrição (Whisper)
        print("\n[3/5] Acionando o Transcritor (Whisper Word-Level)...")
        timestamps = extrair_timestamps(audio_path)
        if not timestamps:
            raise ValueError("A transcrição falhou ou não encontrou palavras.")
            
        # 4. Editor Visual & Metadados
        print("\n[4/5] Gerando metadados de SEO para o YouTube...")
        metadados = gerar_metadados_youtube(tema_ou_url, url_origem=url_origem)
        print(f"Título gerado: {metadados.get('titulo')}")
        
        print(f"\n[4.5/5] Acionando o Editor Visual (Roteador -> {nome_template})...")
        video_final = montar_video_splitscreen(audio_path, timestamps, json_roteiro=json_roteiro, nome_template=nome_template)
        
        # 5. Publicador (YouTube Data API)
        print("\n[5/5] Acionando o Publicador (Upload no YouTube)...")
        response_yt = fazer_upload(video_final, metadados)
        video_id = response_yt.get('id')
        if not video_id:
            raise ValueError("O upload falhou ou não retornou um ID de vídeo válido.")
        
        # 6. Gravação do Estado
        print("\n[Registrando no Banco de Dados]...")
        registrar_upload(tema_ou_url, metadados.get('titulo', ''), video_id)
        
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
    import random
    
    # Lista de tópicos fallback para quando a tarefa rodar 100% autônoma (via Task Scheduler)
    topicos_autonomos = [
        "A farsa do sistema financeiro tradicional e a ilusão de trabalhar 8 horas por dia",
        "Por que o foco extremo é a única habilidade que te salva da mediocridade",
        "A verdade sobre automação de negócios e renda passiva na nova economia",
        "Biohacking: como 1 hora de sono a mais gera 10 mil reais a mais na sua conta",
        "Como a IA está extinguindo o trabalhador mediano em tempo real"
    ]
    
    if len(sys.argv) > 1:
        # Se passado como argumento na linha de comando
        input_str = sys.argv[1]
    elif sys.stdout.isatty():
        # Se rodando interativamente no terminal
        try:
            print("\n" + "="*50)
            print("Opção A: Rota Viral (Digite um tema amplo e agressivo)")
            print("Opção B: Máquina de Vendas (Cole uma URL de Landing Page)")
            print("="*50)
            input_str = input("Digite o tema ou URL (deixe em branco para aleatório): ").strip()
            if not input_str:
                input_str = random.choice(topicos_autonomos)
                print(f"Nenhum input detectado. Usando tópico aleatório: {input_str}")
        except EOFError:
            # Em caso de terminais que não suportam input interativo
            input_str = random.choice(topicos_autonomos)
    else:
        # Se rodando em background (Task Scheduler)
        input_str = random.choice(topicos_autonomos)
        
    iniciar_esteira(input_str)
