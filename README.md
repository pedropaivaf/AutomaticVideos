# 🚀 Autonomous Split-Screen AI Podcast Generator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black?style=for-the-badge&logo=openai)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-purple?style=for-the-badge)
![MoviePy](https://img.shields.io/badge/MoviePy-Video_Editing-red?style=for-the-badge)
![Whisper](https://img.shields.io/badge/OpenAI_Whisper-Transcription-green?style=for-the-badge)

Bem-vindo ao **Gerador Autônomo de Shorts (Split-Screen Podcast)**! Este projeto é um pipeline 100% automatizado, criado para gerar vídeos curtos (Shorts/TikTok/Reels) otimizados para retenção extrema. 

Ele aplica engenharia reversa de atenção, misturando gameplay na parte inferior da tela, avatares dinâmicos de podcast na parte superior e legendas cinéticas no centro.

---

## 🔥 Features Principais

- **🧠 O Roteirista Autônomo:** Gera diálogos dinâmicos e agressivos entre dois personagens via LLM (OpenAI / Gemini), focado em humor e ganchos fortes.
- **🗣️ Diretor de Áudio Multi-Voice:** Integra com ElevenLabs para dar voz a cada personagem de forma autêntica. Remove pausas automaticamente para um ritmo frenético.
- **📝 Transcrição e Legendas Cinéticas:** Utiliza Whisper para capturar *timestamps* (word-level) e criar animações de texto com contornos pesados (estilo MrBeast/Alex Hormozi).
- **🎬 Edição Split-Screen Automática:** Combina clipes de fundo (*gameplay* ou vídeos satisfatórios), sobrepõe os avatares (com animações ao falar) e insere as legendas, renderizando tudo via MoviePy.

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em 5 módulos principais:
1. `src/roteirista.py`: Puxa a API do LLM para estruturar o roteiro em JSON.
2. `src/audio_engine.py`: Sintetiza o áudio via ElevenLabs e junta as falas cortando o silêncio.
3. `src/transcritor.py`: Roda Whisper para gerar as marcações temporais das palavras.
4. `src/editor_visual.py`: Orquestra as trilhas de vídeo, imagens e legendas no layout Vertical (1080x1920).
5. `main.py`: O orquestrador central que junta todos os passos em uma execução com um clique.

---

## 🛠️ Como Instalar e Rodar

### 1. Clonar e Configurar o Ambiente
```bash
git clone https://github.com/seu-usuario/autonomous-podcast-video-generator.git
cd autonomous-podcast-video-generator

# Criar ambiente virtual
python -m venv venv
# No Windows
.\venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Chaves de API
Crie um arquivo `.env` na raiz do projeto (como no exemplo `.env.example`) e adicione as suas chaves:
```env
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="AIzaSy..."
ELEVENLABS_API_KEY="sua-chave-aqui"
```

### 3. Adicionar Assets
O projeto espera arquivos multimídia na pasta `assets/`:
- **`assets/images/`**: Imagens dos avatares (ex: `p1.png`, `p2.png`).
- **`assets/broll/`**: Vídeos de gameplay ou fundo para a parte de baixo da tela (formato vertical/adaptável).

### 4. Rodar a Esteira
```bash
python main.py
```
O vídeo final será exportado na pasta `assets/outputs/`.

---

## ⚠️ Requisitos do Sistema
- Uma instalação de **ImageMagick** (Necessário para a renderização de textos do MoviePy).
- Para transcrição rápida do Whisper, recomenda-se uso de GPU (CUDA).

> **Aviso de Autoria:** Todo o core deste projeto foi estruturado para ser robusto e focado em alta conversão de redes sociais. O agente de IA responsável pelos commits assina a autoria deste repo.