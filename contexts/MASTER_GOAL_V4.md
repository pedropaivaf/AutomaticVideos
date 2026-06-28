# 🎯 MASTER GOAL: ARQUITETURA V4 - HOLLYWOOD VISUAL, SCRAPER E TREND HUNTER

## ⚠️ REGRAS ABSOLUTAS E INVIOLÁVEIS
1. **Autoria Inegociável:** TODO E QUALQUER commit gerado deve ter a autoria configurada ESTRITAMENTE para `Pedro Paiva`.
2. **Isolamento de Falhas:** Use blocos `try/except` em todas as requisições web (Scraper e Trend Hunter) para garantir que a esteira noturna nunca quebre.
3. **Validação Contínua:** Execute e teste CADA fase antes de avançar para a próxima.

---

## FASE 1: O Motor Visual "CapCut Style" e B-Rolls
**Objetivo:** Eliminar o fundo azul genérico. Implementar legendas hiper-estilizadas e fundos dinâmicos em loop (Minecraft, Satisfying, Cinematic).
1. **Estrutura de Assets:** Crie a pasta `assets/broll/` com subpastas `minecraft/`, `cinematic/`, `business/`. (O usuário colocará vídeos genéricos lá).
2. **Refatoração Visual (`editor_visual.py` e templates):**
   - **Backgrounds:** O script deve ler a pasta de `broll` correspondente ao tema, escolher um vídeo aleatório, fazer o crop para 9:16 (1080x1920), remover o áudio original e colocar em loop para durar o tempo exato do roteiro. Se for uma Landing Page, aplique um efeito de escurecimento (-30% de brilho) para focar na legenda.
   - **Legendas (CapCut Style):** Atualize a geração de texto usando o `TextClip` (MoviePy/ImageMagick). Adicione `stroke_color='black'`, `stroke_width=3` e utilize uma fonte grossa e impactante (ex: Montserrat-Black, Arial Black ou TheBoldFont). O texto deve pular palavra por palavra no centro da tela.
   - **Paleta de Cores Dinâmica:** A cor principal da legenda (ex: Amarelo, Verde-Neon, Branco) deve ser um parâmetro que o template recebe.

## FASE 2: Expansão Temporal (Vídeos de 1 Minuto)
**Objetivo:** Permitir que o sistema gere formatos rápidos (30s) ou densos (60s).
1. **Refatoração no `roteirista.py`:**
   - Adicione um parâmetro `duracao="curta"` (padrão) ou `duracao="longa"`.
   - Se `curta`: o prompt do Llama 3.1 deve exigir um roteiro de no máximo 60-70 palavras.
   - Se `longa`: o prompt deve exigir um roteiro denso de 130-150 palavras, com mais agitação da dor e retenção no meio.

## FASE 3: O Extrator de Landing Pages (Business to Video)
**Objetivo:** Transformar qualquer URL em um anúncio em vídeo perfeitamente contextualizado.
1. **Dependências:** Adicione `beautifulsoup4` e `requests` ao ambiente.
2. **Criação do `extrator_url.py`:**
   - Crie a função `raspar_landing_page(url)`. Ela deve extrair o texto principal (H1, H2, parágrafos de dor/solução) ignorando headers/footers.
   - **Extração de Identidade Visual:** Tente extrair a cor predominante (buscando tags de CSS de background ou botões primários) para passar como parâmetro para a cor da legenda. Se falhar, use "Amarelo" ou "Branco" como fallback.
3. **Integração de Contexto:** A IA deve ler o texto da URL, gerar a copy focada em conversão, usar o template visual `cinematic` (ou `business`) e colocar o CTA no vídeo.

## FASE 4: O Caçador de Tendências (Trend Hunter)
**Objetivo:** Autonomia total na escolha de temas virais atualizados.
1. **Dependências:** Adicione bibliotecas para leitura de RSS (`feedparser`) ou o `pytrends` (escolha a opção mais estável para evitar rate-limit).
2. **Criação do `trend_hunter.py`:**
   - Crie `buscar_assunto_viral_do_dia(nicho="tecnologia e negócios")`.
   - A IA deve vasculhar os assuntos mais comentados das últimas 24h e retornar uma string limpa (ex: "A nova IA da Apple que está substituindo programadores").
   - **Fallback:** Se a internet falhar, retorne um assunto padrão de uma lista local focada nos softwares do usuário (Produtividade, Deep Work, Gestão).

## FASE 5: O Orquestrador Interativo (`main.py`)
**Objetivo:** Amarrar todas as novidades com um menu de comando limpo.
1. O `main.py` agora deve oferecer 3 rotas claras caso rodado manualmente:
   - `[1] Trend Hunter Automático` (Roda o caçador, gera vídeo viral sobre o que está em alta, usa b-roll de Minecraft/Satisfatório).
   - `[2] URL to Video` (Pede uma URL, raspa a página, gera vídeo de conversão com b-roll Cinematic).
   - `[3] Tema Manual` (Pede um tema e a duração desejada: 30s ou 60s).
2. **Modo Fantasma (Task Scheduler):** Se rodado via `.bat`, ele deve assumir a Rota 1 (Trend Hunter) silenciosamente.
3. **Commit Final:** Se todos os testes passarem perfeitamente, assine o commit com `feat: implementa arquitetura v4 com scraper, trend hunter e visual capcut`.