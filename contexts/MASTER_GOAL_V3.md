# 🎯 MASTER GOAL: ARQUITETURA V3 - MOTOR DE TEMPLATES E URL-TO-SHORT

## ⚠️ REGRAS ABSOLUTAS E INVIOLÁVEIS (LEIA ANTES DE COMEÇAR)
1. **Autoria Inegociável:** TODO E QUALQUER commit gerado neste repositório deve ter a autoria configurada ESTRITAMENTE para `Pedro Paiva`.
2. **Execução em Blocos:** Você está estritamente proibido de tentar codar todas as fases de uma vez. Execute a FASE 1, faça um teste simulado (mock) para garantir que não quebrou a versão anterior. Só avance para a FASE 2 quando a anterior estiver perfeita.
3. **Resiliência:** Mantenha os blocos `try/except` globais. O sistema não pode crashar no meio da madrugada.

---

## FASE 1: Refatoração para o "Motor de Templates"
**Objetivo:** Desacoplar a edição visual fixa (Podcast Minecraft) do `editor_visual.py` para permitir múltiplos formatos.
1. Crie uma pasta `src/templates/`.
2. Extraia toda a lógica de "Split-Screen" (Avatares + B-roll embaixo) que está hoje no `editor_visual.py` e mova para um arquivo `src/templates/podcast_split.py`.
3. O `editor_visual.py` agora será apenas um **Roteador**. Ele receberá o `audio_path`, `timestamps`, `json_roteiro` e uma nova variável `nome_template`. Baseado no `nome_template`, ele chama o arquivo correspondente na pasta `templates/`.
4. **Validação Fase 1:** Rode um teste passando o template `podcast_split` para garantir que o vídeo original continua sendo gerado perfeitamente.

## FASE 2: Criação do Template "Cinematic B-Roll" (Alta Conversão)
**Objetivo:** Criar a estrutura visual para os vídeos de Landing Pages e virais focados em estética.
1. Crie o arquivo `src/templates/cinematic_broll.py`.
2. **Lógica Visual:** Este template NÃO usa avatares. Ele pega um ou mais vídeos aleatórios da pasta `assets/broll/`, corta (crop) para 1080x1920 (Shorts), coloca em tela cheia e aplica um leve escurecimento (color overlay ou brilho -20%) para dar destaque ao texto.
3. As legendas cinéticas (grossas e amarelas) continuam exatamente no centro da tela.
4. **Validação Fase 2:** Crie um mock passando o template `cinematic_broll` e garanta que o MoviePy renderiza o vídeo em tela cheia com a legenda.

## FASE 3: A Máquina de URL (O Raspador de Landing Pages)
**Objetivo:** Extrair a dor e a solução de qualquer site de vendas.
1. Adicione `beautifulsoup4` e `requests` ao `requirements.txt`.
2. Crie o arquivo `src/extrator_url.py`.
3. Crie a função `raspar_landing_page(url)`. Ela deve acessar a URL, remover tags desnecessárias (scripts, nav, footers) e retornar um texto limpo focando nos Headings (H1, H2, H3) e parágrafos principais. (Até uns 2000 caracteres de puro suco de copy).

## FASE 4: O Novo Cérebro do Roteirista (`roteirista.py`)
**Objetivo:** Adaptar a IA para ser Copywriter de URLs e Diretora de Arte.
1. Crie a função `gerar_roteiro_de_url(texto_raspado)`. O prompt deve instruir o LLM a agir como um Copywriter de Resposta Direta. Ele deve ler o texto da página, identificar o produto e gerar um roteiro de 30-40 segundos: Gancho Agressivo (Dor) -> Agitação -> Solução (O Produto).
2. Atualize a função de metadados (`gerar_metadados_youtube`) para que, quando o vídeo for de URL, o Link da Landing Page seja o CTA inserido obrigatoriamente na primeira linha da descrição.
3. Adicione uma lógica de IA (ou aleatoriedade inteligente) no fluxo: ao receber um `tema` de texto comum, o LLM deve escolher qual template usar (`podcast_split` ou `cinematic_broll`) dependendo do tom (ex: fofoca/conversa = podcast; negócios/motivação = cinematic).

## FASE 5: O Orquestrador Final (`main.py`)
**Objetivo:** Plugar todas as novas esteiras no ciclo mestre.
1. Modifique a entrada da esteira. O input agora pode ser um `tema` (texto viral) OU uma `url` (Landing Page).
2. **Fluxo Condicional:**
   - `SE input.startswith("http"):`
     -> Chama extrator de URL -> Roteirista de URL -> Áudio -> Transcrição -> Template `cinematic_broll` -> YouTube Privado -> Supabase.
   - `SENÃO:`
     -> Checa Supabase -> Roteirista Comum (IA escolhe template) -> Áudio -> Transcrição -> Roteador de Template -> YouTube Privado -> Supabase.
3. **Teste Final:** Execute um teste E2E com uma URL fictícia (ou real) e um texto normal.
4. **O Grand Finale (Commit):** Se tudo funcionar, gere o commit estritamente com a autoria de `Pedro Paiva` com a mensagem: `feat: implementa motor de templates visuais e esteira de conversao url-to-short v3`.