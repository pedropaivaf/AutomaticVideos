import requests
from bs4 import BeautifulSoup

def raspar_landing_page(url: str) -> dict:
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
        
        cor_predominante = "yellow"
        # Tenta extrair alguma cor de botões para usar de base
        botoes = soup.find_all(['button', 'a'])
        for btn in botoes:
            style = btn.get('style', '')
            if 'background-color' in style or 'background' in style:
                if 'blue' in style.lower(): cor_predominante = "blue"
                elif 'green' in style.lower(): cor_predominante = "green"
                elif 'red' in style.lower(): cor_predominante = "red"
                elif 'black' in style.lower(): cor_predominante = "black"
                elif 'white' in style.lower(): cor_predominante = "white"
                
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
            
        print(f"Raspagem concluída. Foram extraídos {len(texto_limpo)} caracteres. Cor predominante: {cor_predominante}")
        return {"texto": texto_limpo, "cor_predominante": cor_predominante}
    except Exception as e:
        print(f"Erro ao raspar a página '{url}': {e}")
        return {"texto": "", "cor_predominante": "yellow"}

if __name__ == "__main__":
    # Teste
    texto = raspar_landing_page("https://example.com")
    print(f"Texto extraído: {texto}")
