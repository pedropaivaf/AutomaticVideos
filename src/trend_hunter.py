import feedparser
import random

def buscar_assunto_viral_do_dia(nicho="tecnologia e negócios") -> str:
    """
    Busca o assunto mais viral usando feeds RSS. Retorna uma string pronta para ser usada como tema.
    """
    print(f"Iniciando caçada de tendências para o nicho: {nicho}")
    
    topicos_fallback = [
        "A farsa do sistema financeiro tradicional e a ilusão de trabalhar 8 horas por dia",
        "Por que o foco extremo é a única habilidade que te salva da mediocridade",
        "A verdade sobre automação de negócios e renda passiva na nova economia",
        "Biohacking: como 1 hora de sono a mais gera 10 mil reais a mais na sua conta",
        "Como a IA está extinguindo o trabalhador mediano em tempo real"
    ]
    
    feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml"
    ]
    
    titulos = []
    try:
        for url in feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                if hasattr(entry, 'title'):
                    titulos.append(entry.title)
                    
        if titulos:
            assunto = random.choice(titulos)
            print(f"Assunto viral encontrado: {assunto}")
            return f"Últimas notícias do mercado: {assunto} e como isso afeta você"
        else:
            raise ValueError("Nenhuma notícia encontrada nos feeds.")
            
    except Exception as e:
        print(f"Falha na busca RSS ({e}). Usando fallback.")
        return random.choice(topicos_fallback)

if __name__ == "__main__":
    tema = buscar_assunto_viral_do_dia()
    print(f"Tema escolhido: {tema}")
