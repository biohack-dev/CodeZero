# CodeZero - Assistente Especialista em Desenvolvimento de Sistemas

> **Um assistente inteligente especializado em desenvolvimento de software, arquitetura de sistemas e codificação.**

## 📋 Sobre o Projeto

CodeZero é um assistente virtual desenvolvido para auxiliar profissionais e estudantes de desenvolvimento de sistemas. Com uma personalidade de mentor sênior, ele oferece respostas objetivas e práticas sobre arquitetura de software, programação, bancos de dados, DevOps e muito mais.

### 🎯 Características Principais

- **Especialista em Desenvolvimento**: Domínio em arquitetura de software, padrões de projeto, backend, frontend, bancos de dados, DevOps e segurança
- **Memória Persistente**: Reconhece usuários, projetos e tecnologias mencionadas
- **Contexto Inteligente**: Detecta automaticamente o contexto da conversa
- **Interface Amigável**: Design responsivo e compatível com navegadores antigos
- **Comandos Especiais**: Acesso rápido a notícias e funcionalidades específicas

## 🚀 Tecnologias

- **Backend**: Python 3.6+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **IA**: Mistral AI API (Mistral Large)
- **Armazenamento**: Pickle + JSON para memória persistente
- **Web Scraping**: BeautifulSoup4 para notícias

## 📦 Instalação

### Pré-requisitos

- Python 3.6 ou superior
- Pip (gerenciador de pacotes Python)

### Passos de Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/codezero.git
cd codezero

# Instale as dependências
pip install flask requests beautifulsoup4 lxml

# Configure sua chave API do Mistral AI
# Edite o arquivo code_zero.py e substitua a variável API_KEY
```

### Execução

```bash
python code_zero.py
```

O servidor será iniciado em `http://localhost:80`

## 💬 Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/help` | Exibe a lista de comandos disponíveis |
| `/tech` | Mostra notícias recentes sobre tecnologia |
| `/mundo` | Exibe notícias mundiais em destaque |
| `/news [tema]` | Busca notícias sobre um tema específico |
| `/clear` | Limpa o histórico visual da conversa |

## 🧠 Recursos de Memória

O CodeZero mantém um histórico persistente de conversas e extrai automaticamente:

- **Nome do usuário**: Detectado através de frases como "meu nome é..."
- **Linguagens de programação**: Python, JavaScript, Java, etc.
- **Frameworks**: React, Django, Flask, etc.
- **Bancos de dados**: MySQL, PostgreSQL, MongoDB, etc.
- **Projetos**: Nomes de projetos mencionados na conversa
- **Contexto**: Identifica o tópico atual (backend, frontend, API, etc.)

## 🎨 Interface

- **Compatível com Firefox ESR 128** e Windows 7
- Design escuro para reduzir fadiga visual
- Responsivo para dispositivos móveis
- Mensagens com formatação Markdown para melhor legibilidade
- Indicador de digitação para feedback visual

## 🔧 Configuração

### Chave API do Mistral AI

O CodeZero utiliza a API do Mistral AI. Para configurar:

1. Obtenha uma chave API em [Mistral AI](https://mistral.ai)
2. Substitua a variável `API_KEY` no código:

```python
API_KEY = "sua-chave-api-aqui"
```

### Personalização

- **Modelo**: Altere `MODEL` para usar diferentes modelos Mistral
- **Temperatura**: Ajuste `temperature` para controlar criatividade das respostas
- **Histórico**: Modifique `max_history_length` para alterar tamanho da memória

## 🏗️ Estrutura do Projeto

```
codezero/
├── code_zero.py           # Aplicação principal
├── codezero_memory.brain  # Memória persistente (pickle)
├── codezero_context.json  # Contexto atual (JSON)
└── README.md             # Este arquivo
```

## 🌟 Exemplos de Uso

### Pergunta sobre arquitetura
```
Usuário: "Como aplicar Clean Architecture em um projeto Python?"
CodeZero: [Resposta detalhada sobre Clean Architecture com exemplos Python]
```

### Solicitação de código
```
Usuário: "Preciso de um exemplo de API REST com Flask"
CodeZero: [Código de exemplo com explicações]
```

### Contexto contínuo
```
Usuário 1: "Estou trabalhando no projeto E-commerce"
CodeZero: "Ótimo! Vou lembrar do projeto E-commerce em nossas conversas"

Usuário 2: "Como posso implementar autenticação JWT?"
CodeZero: [Resposta contextualizada sabendo que se trata do projeto E-commerce]
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas alterações (`git commit -m 'Adicionando nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

![Print](codzero.png)

---

**CodeZero v3.1** - *Compatível com Windows 7 / Firefox ESR 128*# CodeZero
