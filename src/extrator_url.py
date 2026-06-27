import requests
from bs4 import BeautifulSoup

def raspar_landing_page(url: str) -> str:
    """
    Acessa a URL fornecida e extrai o texto de tags relevantes (h1, h2, h3, p) 
    para alimentar o Copywriter LLM.
    """
    print(f"Iniciando raspagem da URL: {url}")
    try:
        # User agent básico para evitar bloqueios simples
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove elementos indesejados
        for element in soup(['script', 'style', 'nav', 'footer', 'noscript']):
            element.decompose()
            
        # Extrai tags relevantes
        tags_alvo = ['h1', 'h2', 'h3', 'p']
        textos = []
        for tag in soup.find_all(tags_alvo):
            texto = tag.get_text(strip=True)
            if texto:
                textos.append(texto)
                
        texto_limpo = " ".join(textos)
        
        # Limita a ~3000 caracteres para não estourar tokens do prompt e focar no core da página
        if len(texto_limpo) > 3000:
            texto_limpo = texto_limpo[:3000] + "..."
            
        print(f"Raspagem concluída. Foram extraídos {len(texto_limpo)} caracteres.")
        return texto_limpo
    except Exception as e:
        print(f"Erro ao raspar a página '{url}': {e}")
        return ""

if __name__ == "__main__":
    # Teste
    texto = raspar_landing_page("https://example.com")
    print(f"Texto extraído: {texto}")
