import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

def obter_cliente() -> OpenAI:
    return OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

def gerar_roteiro(tema: str, personagem1: str = "Peter Griffin", personagem2: str = "Stewie", max_falas: int = 10, duracao: str = "curta") -> list:
    """
    Gera um roteiro de podcast em formato JSON entre dois personagens sobre um tema.
    """
    client = obter_cliente()
    if not client:
        print("Erro: OPENAI_API_KEY não configurada no .env")
        return []
        
    if duracao == "longa":
        instrucao_tamanho = "O roteiro deve ser denso e profundo, com cerca de 130-150 palavras no total, com mais agitação da dor e retenção no meio."
    else:
        instrucao_tamanho = "O roteiro deve ser muito curto e rápido, com no máximo 60-70 palavras no total."

    prompt = f"""
Escreva um roteiro de podcast estilo bate-papo dinâmico e de retenção extrema sobre o tema: "{tema}".
Os participantes são {personagem1} e {personagem2}.
Crie aproximadamente {max_falas} falas no total, alternando entre eles.
{instrucao_tamanho}
As falas devem ser diretas, com humor e opiniões fortes (estilo TikTok/Shorts).

Você deve retornar OBRIGATORIAMENTE um JSON com o seguinte formato exato de lista de objetos:
[
  {{"personagem": "{personagem1}", "texto": "Sua fala aqui..."}},
  {{"personagem": "{personagem2}", "texto": "Resposta imediata..."}}
]

Não inclua formatação Markdown (como ```json) ou texto extra fora do JSON.
"""
    try:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {"role": "system", "content": "Você é um roteirista genial especialista em retenção para Shorts/TikTok. Você apenas responde com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            max_tokens=4096
        )
        content = response.choices[0].message.content
        try:
            dados = json.loads(content)
            if isinstance(dados, dict):
                for key, value in dados.items():
                    if isinstance(value, list):
                        return value
                return [dados]
            elif isinstance(dados, list):
                return dados
            else:
                print("Erro: Formato JSON inesperado retornado pela API.")
                return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}\nConteúdo bruto: {content}")
            return []
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return []

def gerar_roteiro_de_url(texto_raspado: str) -> list:
    """
    Age como um Copywriter de Resposta Direta.
    Lê o texto da página e gera um roteiro de 30-40 segundos: Gancho Agressivo -> Agitação -> Solução.
    """
    client = obter_cliente()
    if not client:
        print("Erro: OPENAI_API_KEY não configurada no .env")
        return []
        
    prompt = f"""
Atue como um Copywriter de Resposta Direta focado em retenção para TikTok/Shorts.
Leia o seguinte texto extraído de uma Landing Page:
---
{texto_raspado}
---

Baseado nisso, crie um roteiro narrado por UMA pessoa (um narrador) de no máximo 40 segundos.
A estrutura OBRIGATÓRIA é:
1. Gancho Agressivo (Tocar na Dor central)
2. Agitação (Piorar a dor / Mostrar consequência)
3. Solução (Apresentar o produto/oferta da página como a única saída)

Como a nossa esteira de áudio atual espera o formato de diálogo, vamos colocar o 'Narrador' como personagem.
Você deve retornar OBRIGATORIAMENTE um JSON com o seguinte formato exato de lista de objetos:
[
  {{"personagem": "Narrador", "texto": "Sua fala de gancho agressivo aqui..."}},
  {{"personagem": "Narrador", "texto": "Sua fala de agitação aqui..."}},
  {{"personagem": "Narrador", "texto": "Sua fala de solução aqui..."}}
]

Não inclua formatação Markdown (como ```json) ou texto extra fora do JSON.
"""
    try:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {"role": "system", "content": "Você é um Copywriter brutal para Shorts/TikTok. Você apenas responde com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            max_tokens=4096
        )
        content = response.choices[0].message.content
        try:
            dados = json.loads(content)
            if isinstance(dados, dict):
                for key, value in dados.items():
                    if isinstance(value, list):
                        return value
                return [dados]
            elif isinstance(dados, list):
                return dados
            else:
                return []
        except json.JSONDecodeError:
            return []
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return []

def escolher_template(tema: str) -> str:
    """
    Usa IA (ou fallback aleatório) para escolher se o vídeo será 'podcast_split' ou 'cinematic_broll'.
    """
    client = obter_cliente()
    if not client:
        import random
        return random.choice(["podcast_split", "cinematic_broll"])
        
    prompt = f"""
Analise o tema abaixo e decida qual formato visual de vídeo combina mais:
Tema: "{tema}"

Opções:
- "podcast_split": Para temas que lembram conversa, curiosidades, fofoca, debates, histórias engraçadas.
- "cinematic_broll": Para temas que lembram negócios, motivação, mindset, dinheiro, automação, reflexão séria.

Responda OBRIGATORIAMENTE um JSON:
{{"template": "nome_do_template"}}
"""
    try:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            max_tokens=4096
        )
        dados = json.loads(response.choices[0].message.content)
        template = dados.get("template", "podcast_split")
        if template not in ["podcast_split", "cinematic_broll"]:
            template = "podcast_split"
        return template
    except Exception:
        import random
        return random.choice(["podcast_split", "cinematic_broll"])

def gerar_metadados_youtube(tema: str, url_origem: str = None) -> dict:
    """
    Gera título, descrição e tags para o vídeo do YouTube usando a API da OpenAI.
    """
    client = obter_cliente()
    if not client:
        print("Erro: OPENAI_API_KEY não configurada. Metadados fallback usados.")
        return {
            "titulo": f"Shorts incrível sobre {tema}"[:60],
            "descricao": f"Um vídeo gerado por IA sobre {tema}.\n\nSaiba mais: {url_origem if url_origem else ''}\n\n#shorts",
            "tags": ["ia", "shorts", "viral", "curiosidades"]
        }
        
    link_aura = os.getenv("LINK_AURA", "https://seu-link-aura.com")
    link_negocios = os.getenv("LINK_NEGOCIOS", "https://seu-link-negocios.com")
    
    if url_origem:
        prompt_cta = f"""
Você está criando metadados para um vídeo que resume uma Landing Page (URL: {url_origem}).
O tema ou texto base extraído foi da página acima.

Você deve retornar OBRIGATORIAMENTE um JSON com o seguinte formato:
{{
  "titulo": "Título magnético e viciante (máx 60 caracteres)",
  "descricao": "🚀 Acesse agora a oferta oficial: {url_origem}\\n\\n[Resumo persuasivo do vídeo...]\\n\\n#shorts",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
A primeira linha da 'descricao' DEVE obrigatoriamente ser exatamente a string do CTA com a URL, conforme o exemplo.
As tags devem ser um array de 5 a 8 strings altamente relevantes.
Não inclua formatação Markdown (como ```json).
"""
    else:
        prompt_cta = f"""
Crie metadados otimizados para YouTube Shorts sobre o tema: "{tema}".
Atue como um Copywriter de conversão de elite.
Primeiro, classifique o tema em uma das duas categorias abaixo para escolher o CTA:

Categoria A (Mindset, Biohacking, Foco, Procrastinação):
CTA: "🧠 Destrua a mediocridade e ative seu Foco Extremo. Acesse o AURA e domine o Deep Work: {link_aura}"

Categoria B (Dinheiro, Automação, Fuga da Matrix, Negócios de Alta Renda):
CTA: "⚙️ Pare de trocar tempo por dinheiro. Tenha seu próprio negócio automatizado hoje rodando no automático: {link_negocios}"

Você deve retornar OBRIGATORIAMENTE um JSON com o seguinte formato:
{{
  "titulo": "Título magnético e viciante (máx 60 caracteres)",
  "descricao": "[INSERIR_O_CTA_ESCOLHIDO_AQUI]\\n\\n[Resumo persuasivo do vídeo...]\\n\\n#shorts",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
A chave 'descricao' DEVE obrigatoriamente começar com a string exata do CTA da categoria correspondente na PRIMEIRA linha.
As tags devem ser um array de 5 a 8 strings altamente relevantes.
Não inclua formatação Markdown (como ```json).
"""

    try:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {"role": "system", "content": "Você é um especialista em SEO para YouTube Shorts. Responda apenas com JSON válido."},
                {"role": "user", "content": prompt_cta}
            ],
            response_format={ "type": "json_object" },
            max_tokens=4096
        )
        content = response.choices[0].message.content
        dados = json.loads(content)
        
        # Garante que a descrição termine com #shorts
        if "#shorts" not in dados.get("descricao", "").lower():
            dados["descricao"] = dados.get("descricao", "") + "\n\n#shorts"
            
        return dados
    except Exception as e:
        print(f"Erro ao gerar metadados: {e}")
        return {
            "titulo": f"Shorts incrível sobre {tema}"[:60],
            "descricao": f"Um vídeo gerado por IA sobre {tema}.\n\nSaiba mais: {url_origem if url_origem else link_aura}\n\n#shorts",
            "tags": ["ia", "shorts", "viral", "curiosidades"]
        }
