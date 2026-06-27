import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

def gerar_roteiro(tema: str, personagem1: str = "Peter Griffin", personagem2: str = "Stewie", max_falas: int = 10) -> list:
    """
    Gera um roteiro de podcast em formato JSON entre dois personagens sobre um tema.
    
    Args:
        tema (str): O assunto principal do podcast.
        personagem1 (str): Nome do primeiro personagem.
        personagem2 (str): Nome do segundo personagem.
        max_falas (int): Quantidade aproximada de linhas de diálogo.
        
    Returns:
        list: Lista de dicionários contendo o roteiro estruturado.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sua_chave_aqui":
        print("Erro: OPENAI_API_KEY não configurada no .env")
        return []
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
Escreva um roteiro de podcast estilo bate-papo dinâmico e de retenção extrema sobre o tema: "{tema}".
Os participantes são {personagem1} e {personagem2}.
Crie aproximadamente {max_falas} falas no total, alternando entre eles.
As falas devem ser curtas, diretas, com humor e opiniões fortes (estilo TikTok/Shorts).

Você deve retornar OBRIGATORIAMENTE um JSON com o seguinte formato exato de lista de objetos:
[
  {{"personagem": "{personagem1}", "texto": "Sua fala aqui..."}},
  {{"personagem": "{personagem2}", "texto": "Resposta imediata..."}}
]

Não inclua formatação Markdown (como ```json) ou texto extra fora do JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um roteirista genial especialista em retenção para Shorts/TikTok. Você apenas responde com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content
        
        # A OpenAI pode retornar o array encapsulado em um objeto se usarmos json_object, 
        # então vamos tentar garantir que retornamos a lista corretamente.
        try:
            dados = json.loads(content)
            # Se a API retornar um dicionário encapsulando a lista, tentamos extrair.
            if isinstance(dados, dict):
                for key, value in dados.items():
                    if isinstance(value, list):
                        return value
                # Se não encontrar lista, tenta adaptar
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

def gerar_metadados_youtube(tema: str) -> dict:
    """
    Gera título, descrição e tags para o vídeo do YouTube usando a API da OpenAI.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sua_chave_aqui":
        print("Erro: OPENAI_API_KEY não configurada. Metadados fallback usados.")
        return {
            "titulo": f"Shorts incrível sobre {tema}"[:60],
            "descricao": f"Um podcast gerado por IA sobre {tema}. #shorts",
            "tags": ["ia", "shorts", "podcast", "viral", "curiosidades"]
        }
        
    client = OpenAI(api_key=api_key)
    
    link_aura = os.getenv("LINK_AURA", "https://seu-link-aura.com")
    link_negocios = os.getenv("LINK_NEGOCIOS", "https://seu-link-negocios.com")
    
    prompt = f"""
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em SEO para YouTube Shorts. Responda apenas com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
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
            "descricao": f"Um podcast gerado por IA sobre {tema}. #shorts",
            "tags": ["ia", "shorts", "podcast", "viral", "curiosidades"]
        }


if __name__ == "__main__":
    # Teste de execução isolada do Módulo 1
    tema_teste = "A teoria da simulação e finanças"
    roteiro = gerar_roteiro(tema_teste, "Personagem1", "Personagem2", 4)
    print("Resultado do Roteirista (JSON):")
    print(json.dumps(roteiro, indent=2, ensure_ascii=False))
