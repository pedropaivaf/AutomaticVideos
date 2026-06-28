import os
import sys
import glob
import random

from src.roteirista import gerar_roteiro, gerar_roteiro_de_url, escolher_template, gerar_metadados_youtube
from src.audio_engine import gerar_audio_dialogo
from src.transcritor import extrair_timestamps
from src.editor_visual import montar_video_splitscreen
from src.publicador import fazer_upload
from src.banco_dados import verificar_tema_existente, registrar_upload
from src.extrator_url import raspar_landing_page
from src.trend_hunter import buscar_assunto_viral_do_dia

def limpar_arquivos_temporarios():
    """Remove lixos de arquivos que podem ter ficado pela metade em caso de crash."""
    print("Executando limpeza de emergência...")
    for temp_file in glob.glob("temp_*.mp3"):
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Não foi possível remover o arquivo {temp_file}: {e}")
            
def iniciar_esteira(input_str: str, rota: int = 3, duracao: str = "curta"):
    """
    Inicia a esteira de vídeos. Recebe um tema textual ou uma URL.
    """
    print("="*50)
    print("🚀 INICIANDO ESTEIRA DO GERADOR DE SHORTS AUTÔNOMO V4 🚀")
    print(f"Rota Ativa: {rota} | Input: {input_str}")
    print("="*50)
    
    is_url = (rota == 2)
    
    try:
        if is_url:
            print("\n[Fluxo URL-to-Video Ativado]")
            
            # 0. Verificação de Memória (Supabase) baseada na URL
            print("\n[0/5] Checando Banco de Dados (Supabase) para a URL...")
            if verificar_tema_existente(input_str):
                print("\033[91m[!] URL já processada no banco de dados. Encerrando operação para evitar redundância.\033[0m")
                sys.exit(0)
                
            # 1. Extrator e Roteiro de URL
            print("\n[1/5] Extraindo conteúdo da URL...")
            dados_pagina = raspar_landing_page(input_str)
            texto_raspado = dados_pagina.get("texto")
            cor_legenda = dados_pagina.get("cor_predominante", "yellow")
            
            if not texto_raspado:
                raise ValueError("A raspagem da URL falhou ou não retornou texto.")
                
            print("\n[1.5/5] Acionando o Roteirista (Copywriter de Resposta Direta)...")
            json_roteiro = gerar_roteiro_de_url(texto_raspado)
            if not json_roteiro:
                raise ValueError("O roteiro de URL falhou ao ser gerado ou retornou vazio.")
                
            nome_template = "cinematic_broll"
            tema_broll = "business"
            is_landing_page = True
            
            # 2. Áudio
            print("\n[2/5] Acionando o Diretor de Áudio (ElevenLabs)...")
            audio_path = gerar_audio_dialogo(json_roteiro, personagem1="Narrador", personagem2="None")
            
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
            if rota == 1:
                nome_template = "cinematic_broll"
                tema_broll = random.choice(["minecraft", "cinematic"])
            else:
                nome_template = escolher_template(input_str)
                tema_broll = "cinematic" if nome_template == "cinematic_broll" else "minecraft"
                
            cor_legenda = "yellow"
            is_landing_page = False
            
            print(f"-> A IA escolheu o template visual: {nome_template} com B-Roll de {tema_broll}")
            
            json_roteiro = gerar_roteiro(input_str, personagem1="Personagem1", personagem2="Personagem2", max_falas=6, duracao=duracao)
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
        video_final = montar_video_splitscreen(
            audio_path, timestamps, json_roteiro=json_roteiro, nome_template=nome_template,
            tema_broll=tema_broll, cor_legenda=cor_legenda, is_landing_page=is_landing_page
        )
        
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
    if len(sys.argv) > 1:
        # Se passado como argumento na linha de comando ou Task Scheduler (.bat)
        # Modo Fantasma assume a Rota 1 (Trend Hunter)
        print("Executando em Modo Fantasma (Rota 1: Trend Hunter)...")
        input_str = buscar_assunto_viral_do_dia()
        iniciar_esteira(input_str, rota=1)
    elif sys.stdout.isatty():
        # Se rodando interativamente no terminal
        try:
            print("\n" + "="*50)
            print("[1] Trend Hunter Automático")
            print("[2] URL to Video")
            print("[3] Tema Manual")
            print("="*50)
            escolha = input("Escolha a rota (1, 2 ou 3): ").strip()
            
            if escolha == "1":
                input_str = buscar_assunto_viral_do_dia()
                iniciar_esteira(input_str, rota=1)
            elif escolha == "2":
                input_str = input("Digite a URL da Landing Page: ").strip()
                iniciar_esteira(input_str, rota=2)
            elif escolha == "3":
                input_str = input("Digite o tema manual: ").strip()
                duracao = input("Duração? (curta/longa) [padrão: curta]: ").strip()
                if not duracao: duracao = "curta"
                iniciar_esteira(input_str, rota=3, duracao=duracao)
            else:
                print("Escolha inválida, assumindo Rota 1 (Trend Hunter).")
                input_str = buscar_assunto_viral_do_dia()
                iniciar_esteira(input_str, rota=1)
        except EOFError:
            # Em caso de terminais que não suportam input interativo
            input_str = buscar_assunto_viral_do_dia()
            iniciar_esteira(input_str, rota=1)
    else:
        # Se rodando em background
        input_str = buscar_assunto_viral_do_dia()
        iniciar_esteira(input_str, rota=1)
