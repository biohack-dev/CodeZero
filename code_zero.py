"""
CodeZero - Assistente Especialista em Desenvolvimento de Sistemas
Versao 3.1 - Compativel com Windows 7 / Firefox ESR 128
"""

from flask import Flask, request, jsonify, render_template_string
import json
import re
import os
import pickle
import warnings
from datetime import datetime
import requests
import urllib.parse
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request

warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)

# ===== CONFIGURACAO MISTRAL AI =====
API_KEY = "rlpDuSpi9iA4IuiGHD0TFX0kBQXALH7Y"
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-large-latest"

MEMORY_FILE = "codezero_memory.brain"
CONTEXT_FILE = "codezero_context.json"


# ===== MEMORIA DE CONVERSA =====

class CodeZeroMemory:
    def __init__(self, memory_file=MEMORY_FILE, context_file=CONTEXT_FILE):
        self.memory_file = memory_file
        self.context_file = context_file
        self.conversation_history = []
        self.known_projects = []
        self.known_tech_stack = []
        self.programming_languages = []
        self.known_frameworks = []
        self.known_databases = []
        self.active_context = ""
        self.max_history_length = 50
        self.user_name = None
        self.load_memory()

    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "rb") as f:
                    data = pickle.load(f)
                self.known_projects = data.get("projects", [])
                self.known_tech_stack = data.get("tech_stack", [])
                self.programming_languages = data.get("languages", [])
                self.known_frameworks = data.get("frameworks", [])
                self.known_databases = data.get("databases", [])
                self.conversation_history = data.get("history", [])
                self.user_name = data.get("user_name", None)

            if os.path.exists(self.context_file):
                with open(self.context_file, "r", encoding="utf-8") as f:
                    ctx = json.load(f)
                    self.active_context = ctx.get("active_context", "")
        except Exception:
            self.conversation_history = []
            self.known_projects = []
            self.known_tech_stack = []
            self.programming_languages = []
            self.known_frameworks = []
            self.known_databases = []
            self.active_context = ""
            self.user_name = None
            self.save_memory()

    def save_memory(self):
        try:
            with open(self.memory_file, "wb") as f:
                pickle.dump({
                    "history": self.conversation_history[-self.max_history_length:],
                    "projects": self.known_projects,
                    "tech_stack": self.known_tech_stack,
                    "languages": self.programming_languages,
                    "frameworks": self.known_frameworks,
                    "databases": self.known_databases,
                    "user_name": self.user_name
                }, f)

            with open(self.context_file, "w", encoding="utf-8") as f:
                json.dump({"active_context": self.active_context}, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_interaction(self, user, bot):
        self.conversation_history.append({"user": user, "bot": bot})
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        self.extract_user_name(user)
        self.extract_tech_info(user)
        self.detect_context(user)
        self.save_memory()

    def extract_user_name(self, text):
        padroes = [
            r"meu nome e (\w+)", r"eu me chamo (\w+)", 
            r"pode me chamar de (\w+)", r"eu sou o (\w+)",
            r"eu sou a (\w+)", r"me chamo (\w+)"
        ]
        t = text.lower()
        for p in padroes:
            m = re.search(p, t)
            if m:
                self.user_name = m.group(1).capitalize()
                return

    def extract_tech_info(self, text):
        t = text.lower()
        
        langs = {
            "python": "Python", "javascript": "JavaScript", "java": "Java",
            "c#": "C#", "c++": "C++", "php": "PHP", "ruby": "Ruby",
            "go": "Go", "rust": "Rust", "typescript": "TypeScript",
            "swift": "Swift", "kotlin": "Kotlin", "scala": "Scala",
            "perl": "Perl", "r": "R", "sql": "SQL", "html": "HTML",
            "css": "CSS", "bash": "Bash", "shell": "Shell"
        }
        for k, v in langs.items():
            if k in t:
                if v not in self.programming_languages:
                    self.programming_languages.append(v)
        
        frameworks = {
            "react": "React", "vue": "Vue.js", "angular": "Angular",
            "node": "Node.js", "django": "Django", "flask": "Flask",
            "spring": "Spring", "laravel": "Laravel", "rails": "Rails",
            "express": "Express", "fastapi": "FastAPI", "next": "Next.js",
            "nuxt": "Nuxt.js", "svelte": "Svelte", "tailwind": "Tailwind"
        }
        for k, v in frameworks.items():
            if k in t:
                if v not in self.known_frameworks:
                    self.known_frameworks.append(v)
        
        dbs = {
            "mongodb": "MongoDB", "postgresql": "PostgreSQL",
            "mysql": "MySQL", "redis": "Redis", "sqlite": "SQLite",
            "oracle": "Oracle", "mssql": "SQL Server", "firebase": "Firebase"
        }
        for k, v in dbs.items():
            if k in t:
                if v not in self.known_databases:
                    self.known_databases.append(v)
        
        techs = [
            "docker", "kubernetes", "aws", "azure", "gcp",
            "tensorflow", "pytorch", "grafana", "prometheus",
            "nginx", "apache", "git", "github", "gitlab"
        ]
        for tech in techs:
            if tech in t:
                if tech not in self.known_tech_stack:
                    self.known_tech_stack.append(tech)
        
        project_patterns = [
            r"projeto (\w+)", r"estou trabalhando em (\w+)", 
            r"meu projeto (\w+)", r"desenvolvendo (\w+)",
            r"criando (\w+)", r"construindo (\w+)",
            r"projeto chamado (\w+)"
        ]
        for pattern in project_patterns:
            match = re.search(pattern, t)
            if match:
                project = match.group(1).capitalize()
                if project not in self.known_projects:
                    self.known_projects.append(project)

    def detect_context(self, text):
        t = text.lower()
        contexts = {
            "backend": "Backend",
            "frontend": "Frontend",
            "fullstack": "Fullstack",
            "api": "API / Microservices",
            "microservicos": "Microservices",
            "arquitetura": "Arquitetura de Software",
            "devops": "DevOps / Infraestrutura",
            "seguranca": "Seguranca da Informacao",
            "performance": "Performance / Otimizacao",
            "mobile": "Mobile Development",
            "data science": "Data Science / IA",
            "machine learning": "Machine Learning",
            "cloud": "Cloud Computing",
            "banco de dados": "Banco de Dados",
            "teste": "Testes / Qualidade"
        }
        for k, v in contexts.items():
            if k in t:
                self.active_context = v
                return

    def get_context(self):
        ctx = []
        if self.user_name:
            ctx.append("O usuario se chama " + self.user_name + ".")
        if self.programming_languages:
            ctx.append("Linguagens conhecidas: " + ", ".join(self.programming_languages) + ".")
        if self.known_frameworks:
            ctx.append("Frameworks mencionados: " + ", ".join(self.known_frameworks) + ".")
        if self.known_databases:
            ctx.append("Bancos de dados: " + ", ".join(self.known_databases) + ".")
        if self.known_tech_stack:
            ctx.append("Tecnologias: " + ", ".join(self.known_tech_stack) + ".")
        if self.known_projects:
            ctx.append("Projetos: " + ", ".join(self.known_projects) + ".")
        if self.active_context:
            ctx.append("Contexto atual: " + self.active_context + ".")
        return " ".join(ctx)


codezero_memory = CodeZeroMemory()


# ===== FUNCOES UTILITARIAS =====

def clean_response(text):
    if not text:
        return text
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def remove_emojis(text):
    if not text:
        return text
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F926-\U0001F937"
        "\U00010000-\U0010FFFF"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'[^\x00-\x7F\u00C0-\u00FF\u0100-\u017F]', '', text)
    return text.strip()


def get_codezero_response(prompt):
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

    system_prompt = """
Voce e o CodeZero, um assistente especialista em desenvolvimento de sistemas e codificacao.

=== SUA PERSONALIDADE ===
- Voce e um mentor senior de desenvolvimento de software
- Tem um tom profissional, mas acessivel e amigavel
- Adora ensinar e compartilhar conhecimento
- E paciente e didatico
- Reconhece que existem multiplas abordagens para resolver problemas

=== SEU CONHECIMENTO ===
- Arquitetura de software (Clean Architecture, DDD, Microservices, etc.)
- Padroes de projeto (GoF, SOLID, etc.)
- Desenvolvimento backend (API, ORM, Autenticacao, etc.)
- Desenvolvimento frontend (React, Vue, SPA, etc.)
- Bancos de dados (SQL, NoSQL, Modelagem, Otimizacao)
- DevOps e Cloud (Docker, Kubernetes, AWS, Azure, GCP)
- Seguranca (OWASP, Boas praticas, Criptografia)
- Performance (Cache, Indexacao, Profiling)
- Engenharia de software (Agile, Git, Code Review, CI/CD)
- Algoritmos e estruturas de dados

=== ESTILO DE RESPOSTA ===
- Responda de forma CURTA e OBJETIVA
- Curtas e diretas
- Objetivas e praticas
- Sem enrolacao
- Sem se apresentar
- Sem cumprimentos desnecessarios
- Va direto ao ponto com a informacao solicitada
- Seja diretO e pratica    
- Use markdown para organizar a informacao:
  ## Titulos principais
  ### Subtitulos
  - Listas para itens
  ```code``` para blocos de codigo
  **negrito** para destaque
  *italico* para enfase

"""

    messages = [{"role": "system", "content": system_prompt}]

    contexto = codezero_memory.get_context()
    if contexto:
        messages.append({"role": "system", "content": "Contexto da conversa: " + contexto})

    for h in codezero_memory.conversation_history[-5:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["bot"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.95,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        resposta = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        resposta = clean_response(resposta)
        resposta = remove_emojis(resposta)

        codezero_memory.add_interaction(prompt, resposta)
        return resposta

    except requests.exceptions.Timeout:
        return """
## Timeout

Desculpe, a API esta demorando para responder. Tente novamente em alguns segundos.
"""
    except requests.exceptions.RequestException as e:
        return """
## Erro de Conexao

Nao foi possivel conectar a API do CodeZero.

**Detalhes do erro:** """ + str(e)
    except Exception as e:
        return """
## Erro Inesperado

Ocorreu um erro ao processar sua solicitacao.

**Erro:** """ + str(e)


def get_tech_news():
    try:
        url = "https://news.google.com/rss/search?q=tecnologia+programacao&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        xml = urlopen(req).read()
        s = soup(xml, "lxml-xml")
        items = []
        for i in s.findAll("item")[:5]:
            title = i.title.text
            if " - " in title:
                title = title.split(" - ")[0]
            items.append(title)
        return items
    except Exception:
        return ["Erro ao buscar noticias de tecnologia."]


def get_news(q):
    try:
        encoded = urllib.parse.quote(q)
        url = "https://news.google.com/rss/search?q=" + encoded + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        xml = urlopen(req).read()
        s = soup(xml, "lxml-xml")
        items = []
        for i in s.findAll("item")[:5]:
            title = i.title.text
            if " - " in title:
                title = title.split(" - ")[0]
            items.append(title)
        return items
    except Exception:
        return ["Erro ao buscar noticias."]


def get_world_news():
    try:
        url = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYQjBMVUpTR2dKQ1VpZ0FQAQ?hl=pt-BR&gl=BR&ceid=BR:pt-419"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        xml = urlopen(req).read()
        s = soup(xml, "lxml-xml")
        items = []
        for i in s.findAll("item")[:5]:
            title = i.title.text
            if " - " in title:
                title = title.split(" - ")[0]
            items.append(title)
        return items
    except Exception:
        return ["Erro ao buscar noticias mundiais."]


# ===== HTML TEMPLATE - COMPATIVEL COM FIREFOX ESR 128 =====

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeZero - Assistente de Desenvolvimento</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #0a0e1a;
            color: #e0e0e0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: #0f1a2e;
            padding: 14px 24px;
            border-bottom: 2px solid #1a3a6a;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header-icon {
            width: 36px;
            height: 36px;
            background: #1a3a6a;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
            color: #4af0ff;
        }
        
        .header h1 {
            font-size: 20px;
            font-weight: 700;
            color: #4af0ff;
        }
        
        .header h1 span {
            color: #7ddfb0;
        }
        
        .header-status {
            font-size: 12px;
            color: #7ddfb0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #7ddfb0;
            display: inline-block;
        }
        
        .status-dot.active {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .chat-container::-webkit-scrollbar {
            width: 4px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #0a0e1a;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #1a3a5a;
            border-radius: 4px;
        }
        
        .message {
            display: flex;
            max-width: 85%;
            flex-direction: column;
        }
        
        .message.user {
            align-self: flex-end;
        }
        .message.codezero {
            align-self: flex-start;
        }
        .message.system {
            align-self: center;
            max-width: 100%;
        }
        
        .message.system .bubble {
            background: #1a2224;
            color: #888;
            font-size: 12px;
            padding: 4px 16px;
            border-radius: 20px;
            text-align: center;
        }
        
        .bubble {
            padding: 12px 18px;
            border-radius: 16px;
            word-wrap: break-word;
            line-height: 1.6;
            font-size: 14px;
        }
        
        .message.user .bubble {
            background: #1a3a5a;
            border: 1px solid #2a6a8a;
            border-radius: 16px 16px 4px 16px;
            color: #d4e8f4;
        }
        
        .message.codezero .bubble {
            background: #0f1a2e;
            border: 1px solid #1a3a5a;
            border-radius: 16px 16px 16px 4px;
            color: #e0e8f0;
        }
        
        .message .meta {
            font-size: 10px;
            color: #4a6a7a;
            margin-top: 4px;
            padding: 0 4px;
        }
        
        .message.user .meta {
            text-align: right;
        }
        .message.codezero .meta {
            text-align: left;
        }
        
        .bubble h1 {
            font-size: 1.5em;
            margin: 10px 0 6px 0;
            color: #4af0ff;
            border-bottom: 2px solid #1a3a5a;
            padding-bottom: 4px;
        }
        
        .bubble h2 {
            font-size: 1.3em;
            margin: 8px 0 4px 0;
            color: #7ddfb0;
            border-bottom: 1px solid #1a3a5a;
            padding-bottom: 3px;
        }
        
        .bubble h3 {
            font-size: 1.1em;
            margin: 6px 0 3px 0;
            color: #5ac8fa;
        }
        
        .bubble h1:first-child,
        .bubble h2:first-child,
        .bubble h3:first-child {
            margin-top: 0;
        }
        
        .bubble code {
            background: #0a1222;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            color: #f4aa55;
            font-family: Consolas, monospace;
        }
        
        .bubble pre {
            background: #0a1222;
            border-left: 3px solid #4af0ff;
            padding: 12px 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
            font-size: 13px;
            font-family: Consolas, monospace;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .bubble pre code {
            background: none;
            padding: 0;
            color: #d4e8f4;
            font-size: inherit;
        }
        
        .bubble ul, .bubble ol {
            margin: 6px 0 6px 20px;
        }
        .bubble li {
            margin: 3px 0;
        }
        .bubble blockquote {
            border-left: 3px solid #4af0ff;
            padding-left: 14px;
            margin: 6px 0;
            color: #8aaabb;
            font-style: italic;
        }
        .bubble hr {
            border: none;
            border-top: 1px solid #1a3a5a;
            margin: 10px 0;
        }
        .bubble a {
            color: #4af0ff;
            text-decoration: none;
            border-bottom: 1px dotted #4af0ff;
        }
        .bubble a:hover {
            border-bottom: 1px solid #4af0ff;
        }
        .bubble strong {
            color: #7ddfb0;
        }
        .bubble em {
            color: #5ac8fa;
        }
        
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 4px 0;
        }
        
        .typing-indicator span {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #4a8aaa;
            display: inline-block;
        }
        
        .typing-indicator span:nth-child(1) {
            animation: typing 1.4s infinite both;
        }
        .typing-indicator span:nth-child(2) {
            animation: typing 1.4s infinite both 0.2s;
        }
        .typing-indicator span:nth-child(3) {
            animation: typing 1.4s infinite both 0.4s;
        }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .input-area {
            background: #0f1a2e;
            border-top: 1px solid #1a3a5a;
            padding: 12px 24px;
            flex-shrink: 0;
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }
        
        .input-wrapper {
            flex: 1;
            background: #0a1222;
            border: 1px solid #1a3a5a;
            border-radius: 24px;
            overflow: hidden;
            display: flex;
            align-items: flex-end;
        }
        
        .input-wrapper:focus-within {
            border-color: #4af0ff;
        }
        
        .input-wrapper textarea {
            flex: 1;
            background: transparent;
            border: none;
            color: #e0e8f0;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 14px;
            padding: 10px 16px;
            resize: none;
            outline: none;
            min-height: 44px;
            max-height: 120px;
            line-height: 1.4;
        }
        
        .input-wrapper textarea::-moz-placeholder {
            color: #3a5a6a;
        }
        .input-wrapper textarea:-ms-input-placeholder {
            color: #3a5a6a;
        }
        .input-wrapper textarea::placeholder {
            color: #3a5a6a;
        }
        
        .btn-send {
            background: #1a3a6a;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            color: #4af0ff;
            font-size: 18px;
            cursor: pointer;
            flex-shrink: 0;
            margin: 4px 6px 4px 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-send svg {
            pointer-events: none;
        }

        .btn-send:hover {
            background: #2a5a8a;
        }
        .btn-send:active {
            transform: scale(0.94);
        }
        .btn-send:disabled {
            opacity: 0.4;
            cursor: default;
        }
        
        .btn-command {
            background: #0a1222;
            border: 1px solid #1a3a5a;
            border-radius: 24px;
            padding: 6px 14px;
            color: #7a9aaa;
            font-size: 12px;
            cursor: pointer;
            font-family: Arial, Helvetica, sans-serif;
            flex-shrink: 0;
            height: 40px;
        }
        
        .btn-command:hover {
            background: #1a2a4a;
            border-color: #4af0ff;
            color: #4af0ff;
        }
        
        .quick-commands {
            display: flex;
            gap: 6px;
            flex-shrink: 0;
        }
        
        .quick-commands .btn-command {
            font-size: 12px;
            padding: 6px 14px;
            height: 44px;
        }
        
        .news-list {
            margin: 6px 0 0 0;
            padding-left: 18px;
        }
        .news-list li {
            margin: 4px 0;
            color: #b0d0c0;
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 10px 16px;
            }
            .header h1 {
                font-size: 16px;
            }
            .header-icon {
                width: 30px;
                height: 30px;
                font-size: 14px;
            }
            .chat-container {
                padding: 12px 16px;
            }
            .input-area {
                padding: 10px 12px;
                flex-wrap: wrap;
            }
            .message {
                max-width: 92%;
            }
            .quick-commands {
                display: none;
            }
            .bubble {
                font-size: 13px;
                padding: 10px 14px;
            }
        }
        
        @media (max-width: 480px) {
            .header-status {
                font-size: 10px;
            }
            .header-status .status-dot {
                width: 6px;
                height: 6px;
            }
            .chat-container {
                padding: 8px 12px;
                gap: 8px;
            }
            .message {
                max-width: 95%;
            }
            .bubble pre {
                font-size: 11px;
                padding: 8px 12px;
            }
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="header-left">
            <div class="header-icon">CZ</div>
            <h1>Code<span>Zero</span></h1>
        </div>
        <div class="header-status">
            <span class="status-dot active" id="statusDot"></span>
            <span id="statusText">Conectado</span>
        </div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="message system">
            <div class="bubble">
                CodeZero iniciado.
                Especialista em desenvolvimento de sistemas e codificacao.
                Digite /help para ver os comandos disponiveis.
            </div>
        </div>
    </div>

    <div class="input-area">
        <div class="quick-commands">
            <button class="btn-command" id="btnHelp" type="button" onclick="sendCommand('/help')">Ajuda</button>
            <button class="btn-command" id="btnTech" type="button" onclick="sendCommand('/tech')">Tech</button>
            <button class="btn-command" id="btnClear" type="button" onclick="clearChat()">Limpar</button>
        </div>
        <div class="input-wrapper">
            <textarea id="msgInput" rows="1" placeholder="Pergunte sobre codigo, arquitetura, sistemas..."></textarea>
            <button class="btn-send" id="sendBtn" type="button" onclick="sendMessage()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
            </button>
        </div>
    </div>

    <script>
        // ===== CODIGO COMPATIVEL COM FIREFOX ESR 128 =====
        
        var chatContainer = document.getElementById('chatContainer');
        var msgInput = document.getElementById('msgInput');
        var sendBtn = document.getElementById('sendBtn');
        var statusText = document.getElementById('statusText');
        var statusDot = document.getElementById('statusDot');
        
        var isWaiting = false;
        var messageId = 0;
        
        // Auto-expand textarea
        msgInput.addEventListener('input', function() {
            this.style.height = 'auto';
            var maxHeight = 120;
            if (this.scrollHeight > maxHeight) {
                this.style.height = maxHeight + 'px';
            } else {
                this.style.height = this.scrollHeight + 'px';
            }
        });
        
        // Enter to send
        msgInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Escapar HTML seguro
        function escapeHtml(text) {
            if (!text) return '';
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Renderizar Markdown
        function renderMarkdown(text) {
            if (!text) return '';
            
            var html = text;
            
            // Blocos de codigo
            html = html.replace(/```(\\w*)\\n?([\\s\\S]*?)```/g, function(match, lang, code) {
                var escapedCode = escapeHtml(code.trim());
                return '<pre><code class="language-' + lang + '">' + escapedCode + '</code></pre>';
            });
            
            // Titulos
            html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
            
            // Negrito e Italico
            html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
            html = html.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
            
            // Codigo inline
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Links
            html = html.replace(/\\[([^\\]]+)\\]\\(([^\\)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
            
            // Listas
            html = html.replace(/^[\\-\\*]\\s+(.+)$/gm, '<li>$1</li>');
            html = html.replace(/(<li>.*<\\/li>\\n?)+/g, function(match) {
                if (match.indexOf('<ul>') !== -1) return match;
                return '<ul>' + match + '</ul>';
            });
            
            // Quebras de linha
            html = html.replace(/\\n/g, '<br>');
            
            return html;
        }
        
        // Adicionar mensagem na tela
        function addMessage(text, type, meta) {
            type = type || 'codezero';
            meta = meta || new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            
            var div = document.createElement('div');
            div.className = 'message ' + type + ' fade-in';
            div.id = 'msg-' + messageId;
            messageId = messageId + 1;
            
            var bubble = document.createElement('div');
            bubble.className = 'bubble';
            
            if (type === 'codezero') {
                bubble.innerHTML = renderMarkdown(text);
            } else {
                bubble.textContent = text;
            }
            
            var metaDiv = document.createElement('div');
            metaDiv.className = 'meta';
            metaDiv.textContent = meta;
            
            div.appendChild(bubble);
            div.appendChild(metaDiv);
            chatContainer.appendChild(div);
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return div;
        }
        
        // Mensagem de Sistema
        function addSystemMessage(text) {
            var div = document.createElement('div');
            div.className = 'message system fade-in';
            var bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = text;
            div.appendChild(bubble);
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return div;
        }
        
        // Indicador de digitacao
        function showTyping() {
            var div = document.createElement('div');
            div.className = 'message codezero';
            div.id = 'typingIndicator';
            var bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            div.appendChild(bubble);
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function hideTyping() {
            var el = document.getElementById('typingIndicator');
            if (el && el.parentNode) {
                el.parentNode.removeChild(el);
            }
        }
        
        function formatNewsList(items) {
            if (!items || items.length === 0) return 'Nenhuma noticia encontrada.';
            var html = '<ul class="news-list">';
            for (var i = 0; i < items.length; i++) {
                html += '<li>' + escapeHtml(items[i]) + '</li>';
            }
            html += '</ul>';
            return html;
        }
        
        function clearChat() {
            chatContainer.innerHTML = '';
            addSystemMessage('Conversa limpa com sucesso!');
        }

        function sendCommand(cmd) {
            msgInput.value = cmd;
            sendMessage();
        }
        
        function sendMessage() {
            var text = msgInput.value.trim();
            
            if (!text || isWaiting) {
                return;
            }
            
            addMessage(text, 'user');
            msgInput.value = '';
            msgInput.style.height = 'auto';
            
            isWaiting = true;
            sendBtn.disabled = true;
            statusText.textContent = 'Pensando...';
            statusDot.className = 'status-dot';
            
            showTyping();
            
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/chat', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    hideTyping();
                    isWaiting = false;
                    sendBtn.disabled = false;
                    statusText.textContent = 'Conectado';
                    statusDot.className = 'status-dot active';
                    
                    if (xhr.status === 200) {
                        try {
                            var data = JSON.parse(xhr.responseText);
                            
                            if (data.error) {
                                addMessage('Erro: ' + escapeHtml(data.error), 'codezero');
                                return;
                            }
                            
                            if (data.type === 'news') {
                                var newsHtml = formatNewsList(data.items);
                                addMessage('Noticias: ' + escapeHtml(data.title) + '<br>' + newsHtml, 'codezero');
                            } else if (data.type === 'system') {
                                addSystemMessage(data.message);
                            } else {
                                addMessage(data.message, 'codezero');
                            }
                        } catch (e) {
                            addMessage('Erro ao processar resposta: ' + e.message, 'codezero');
                        }
                    } else {
                        addMessage('Erro no servidor: ' + xhr.status, 'codezero');
                    }
                    msgInput.focus();
                }
            };
            
            xhr.onerror = function() {
                hideTyping();
                isWaiting = false;
                sendBtn.disabled = false;
                statusText.textContent = 'Erro';
                statusDot.className = 'status-dot';
                addMessage('Erro de conexao com o servidor.', 'codezero');
                msgInput.focus();
            };
            
            try {
                xhr.send(JSON.stringify({ message: text }));
            } catch (e) {
                hideTyping();
                isWaiting = false;
                sendBtn.disabled = false;
                statusText.textContent = 'Erro';
                statusDot.className = 'status-dot';
                addMessage('Erro ao enviar: ' + e.message, 'codezero');
                msgInput.focus();
            }
        }

        // Foco apenas ao clicar diretamente na área limpa do chat
        chatContainer.addEventListener('click', function(e) {
            if (e.target === chatContainer) {
                msgInput.focus();
            }
        });

        // Foco inicial ao carregar a página
        msgInput.focus();
        
        console.log('CodeZero v3.1 carregado com sucesso!');
    </script>

</body>
</html>
"""


# ===== ROTAS =====

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'})
        
        cmd = user_message.lower()
        
        if cmd == '/help':
            help_text = """
            <strong>Comandos disponiveis:</strong><br><br>
            <code>/help</code> - Mostra esta ajuda<br>
            <code>/tech</code> - Noticias de tecnologia<br>
            <code>/mundo</code> - Noticias mundiais<br>
            <code>/news [tema]</code> - Buscar noticias sobre um tema<br>
            <code>/clear</code> - Limpar conversa (apenas visual)<br><br>
            <strong>Dica:</strong> Pergunte sobre desenvolvimento, arquitetura de software, codigo, banco de dados, DevOps, etc.
            """
            return jsonify({'type': 'help', 'message': help_text})
        
        if cmd == '/clear' or cmd == '/cls':
            return jsonify({'type': 'system', 'message': 'Conversa limpa!'})
        
        if cmd == '/tech':
            noticias = get_tech_news()
            return jsonify({
                'type': 'news',
                'title': 'Noticias de Tecnologia',
                'items': noticias
            })
        
        if cmd == '/mundo':
            noticias = get_world_news()
            return jsonify({
                'type': 'news',
                'title': 'Noticias Mundiais',
                'items': noticias
            })
        
        if user_message.startswith('/news '):
            tema = user_message[6:].strip()
            if not tema:
                return jsonify({'error': 'Especifique um tema. Ex: /news python'})
            noticias = get_news(tema)
            return jsonify({
                'type': 'news',
                'title': 'Noticias sobre: ' + tema,
                'items': noticias
            })
        
        resposta = get_codezero_response(user_message)
        return jsonify({'type': 'chat', 'message': resposta})
        
    except Exception as e:
        print("Erro no servidor:", str(e))
        return jsonify({'error': 'Erro no servidor: ' + str(e)})


if __name__ == '__main__':
    print("="*70)
    print(" CodeZero v3.1 - Compativel com Windows 7 / Firefox ESR 128")
    print("="*70)
    print("\n Servidor: http://localhost:80")
    print(" Especialista em Arquitetura, Codificacao e Sistemas")
    print(" Memoria persistente com reconhecimento de contexto")
    print("\n Pressione Ctrl+C para encerrar\n")
    print("="*70)
    app.run(debug=True, host='0.0.0.0', port=80)