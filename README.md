# RAG System - PDF Ingestion and Semantic Search

Sistema de Recuperação Aumentada por Geração (RAG) para busca semântica em documentos PDF usando LangChain e PostgreSQL com pgVector.

## 📋 Visão Geral

Este projeto implementa um sistema RAG completo que:
- Ingere documentos PDF e armazena em banco vetorial
- Permite fazer perguntas via CLI sobre o conteúdo do PDF
- Responde apenas com base no contexto do documento (sem alucinações)

## 🛠️ Tecnologias

- **Python 3.12+**
- **LangChain** - Framework de orquestração
- **PostgreSQL + pgVector** - Banco de dados vetorial
- **Docker & Docker Compose** - Containerização
- **Modelos de Embedding**: OpenAI, Google Gemini, ou HuggingFace (local)
- **LLM**: Google Gemini

## 📁 Estrutura do Projeto

```
├── docker-compose.yml          # Configuração PostgreSQL + pgVector
├── requirements.txt            # Dependências Python
├── .env.example               # Template de variáveis de ambiente
├── src/
│   ├── ingest.py              # Script de ingestão do PDF
│   ├── search.py              # Lógica de busca semântica
│   ├── chat.py                # Interface CLI
│   └── utils.py               # Utilitários (seleção de modelo)
├── document.pdf               # PDF para ingestão
└── README.md                  # Este arquivo
```

---

## 🚀 Setup e Instalação

### 1. Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose instalados
- Git

### 2. Clone o Repositório

```bash
git clone https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

### 3. Crie o Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 4. Instale as Dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração do Ambiente

### 1. Copie o Arquivo de Exemplo

```bash
cp .env.example .env
```

### 2. Configure as Variáveis de Ambiente

Edite o arquivo `.env` com suas configurações:

```bash
# Tipo de modelo de embedding (free, gemini, ou openai)
MODEL_TYPE=free

# Google Gemini (opcional - apenas se MODEL_TYPE=gemini)
GOOGLE_API_KEY=sua_api_key_aqui
GOOGLE_EMBEDDING_MODEL='models/embedding-001'
GOOGLE_GEMINI_MODEL='gemini-2.5-flash-lite'

# OpenAI (opcional - apenas se MODEL_TYPE=openai)
OPENAI_API_KEY=sua_api_key_aqui
OPENAI_EMBEDDING_MODEL='text-embedding-3-small'

# Modelo local gratuito (padrão quando MODEL_TYPE=free)
FREE_EMBEDDING_MODEL='google/embeddinggemma-300m'

# Configuração do Banco de Dados
DATABASE_URL='postgresql://postgres:postgres@localhost:5432/rag'
PG_VECTOR_COLLECTION_NAME='pdf_documents'

# Caminho do PDF
PDF_PATH='document.pdf'
```

### 3. Opções de Modelos de Embedding

Você pode escolher entre três opções configurando `MODEL_TYPE`:

| Opção | Configuração | Vantagens | Desvantagens |
|-------|-------------|-----------|--------------|
| **free** | `MODEL_TYPE=free` | Gratuito, sem API key, roda localmente | Menor qualidade |
| **gemini** | `MODEL_TYPE=gemini` | Alta qualidade, quota gratuita | Requer API key, limites de quota |
| **openai** | `MODEL_TYPE=openai` | Melhor qualidade | Pago, requer API key |

**Recomendação**: Use `free` para desenvolvimento e testes, `gemini` ou `openai` para produção.

---

## 🗄️ Inicialização do Banco de Dados

### 1. Suba o PostgreSQL com pgVector

```bash
docker compose up -d
```

Isso irá:
- Criar um container PostgreSQL com a extensão pgVector
- Expor na porta 5432
- Criar o banco de dados `rag`
- Instalar a extensão `vector` automaticamente

### 2. Verifique se o Banco Está Rodando

```bash
docker ps
```

Você deve ver um container chamado `postgres_rag` rodando.

### 3. (Opcional) Acesse o Banco de Dados

```bash
docker exec -it postgres_rag psql -U postgres -d rag
```

Comandos úteis dentro do psql:
```sql
-- Listar coleções
SELECT * FROM langchain_pg_collection;

-- Verificar extensões instaladas
\dx

-- Sair
\q
```

---

## 📥 Ingestão do PDF

### 1. Coloque seu PDF no Diretório

Certifique-se de que o arquivo `document.pdf` existe no diretório raiz, ou atualize `PDF_PATH` no `.env`.

### 2. Execute o Script de Ingestão

```bash
python src/ingest.py
```

**O que acontece:**
1. Carrega o PDF usando `PyPDFLoader`
2. Divide em chunks de 1000 caracteres (overlap de 150)
3. Gera embeddings para cada chunk
4. Armazena os vetores no PostgreSQL

**Tempo estimado**: 1-5 minutos dependendo do tamanho do PDF e do modelo escolhido.

**Saída esperada:**
```
[Sem erros = sucesso]
```

### 3. Verificação

```bash
docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
```

Você deve ver o número de chunks ingeridos.

---

## 💬 Execução do Chat

### 1. Inicie o Chat Interativo

```bash
python src/chat.py
```

### 2. Faça Perguntas

```
==================================================
Chat com Documentos PDF - Sistema RAG
==================================================
Digite suas perguntas sobre o documento.
Digite 'sair', 'exit' ou 'quit' para encerrar.

Você: Qual é o tema principal do documento?

Buscando informações...

Assistente: [Resposta baseada no conteúdo do PDF]

--------------------------------------------------

Você: sair
Encerrando o assistente. Até logo!
```

### 3. Comportamento Esperado

**Perguntas no contexto** (informações presentes no PDF):
```
Você: Qual o faturamento da empresa?
Assistente: O faturamento foi de 10 milhões de reais.
```

**Perguntas fora do contexto** (informações não presentes no PDF):
```
Você: Qual é a capital da França?
Assistente: Não tenho informações necessárias para responder sua pergunta.
```

---

## 🔄 Fluxo de Trabalho Completo

```bash
# 1. Ative o ambiente virtual
source .venv/bin/activate

# 2. Suba o banco de dados
docker compose up -d

# 3. Configure o .env (se ainda não fez)
cp .env.example .env
# Edite o .env com suas configurações

# 4. Ingira o PDF
python src/ingest.py

# 5. Inicie o chat
python src/chat.py
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'dotenv'"
**Causa**: Não está usando o ambiente virtual ou dependências não instaladas.

**Solução**:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Erro: "429 You exceeded your current quota"
**Causa**: Quota do Google Gemini/OpenAI esgotada.

**Solução**: Mude para modelo local:
```bash
# No .env
MODEL_TYPE=free
```

Depois re-ingira o PDF:
```bash
# Limpe a coleção primeiro
docker exec -it postgres_rag psql -U postgres -d rag -c "DROP TABLE IF EXISTS langchain_pg_embedding CASCADE;"

# Re-ingira
python src/ingest.py
```

### Erro: "Vector dimension mismatch"
**Causa**: Mudou o modelo de embedding sem re-ingerir.

**Solução**: Sempre que mudar `MODEL_TYPE`, re-ingira o PDF:
```bash
# Limpe o banco
docker compose down -v
docker compose up -d

# Aguarde o banco inicializar
sleep 10

# Re-ingira
python src/ingest.py
```

### Erro: "Connection refused" no PostgreSQL
**Causa**: Banco não está rodando ou não terminou de inicializar.

**Solução**:
```bash
# Verifique se está rodando
docker ps

# Se não estiver, inicie
docker compose up -d

# Aguarde a inicialização (healthcheck)
docker compose ps
```

### Banco não conecta mesmo rodando
**Causa**: URL do banco incorreta no `.env`.

**Solução**: Verifique se `DATABASE_URL` está correto:
```bash
DATABASE_URL='postgresql://postgres:postgres@localhost:5432/rag'
```

---

## 🧪 Testando o Sistema

### Teste 1: Pergunta no Contexto
```
Você: [Pergunte algo que ESTÁ no PDF]
Esperado: Resposta precisa baseada no documento
```

### Teste 2: Pergunta Fora do Contexto
```
Você: Qual é a capital da França?
Esperado: "Não tenho informações necessárias para responder sua pergunta."
```

### Teste 3: Pergunta Vaga
```
Você: Me fale sobre isso
Esperado: Resposta baseada no contexto geral do documento
```

---

## 📝 Notas Importantes

1. **Troca de Modelo**: Sempre re-ingira o PDF ao mudar `MODEL_TYPE`
2. **Performance**: Modelos locais (`free`) são mais lentos mas gratuitos
3. **Segurança**: Nunca commite o arquivo `.env` com suas API keys
4. **Limites**: Google Gemini free tier tem limite de requisições por minuto
5. **Custos**: OpenAI cobra por uso de embeddings e LLM

---

## 🤝 Contribuindo

Este é um projeto acadêmico do MBA Full Cycle. Para contribuir:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças seguindo [Conventional Commits](.github/git-instructions.md)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é parte do MBA Engenharia de Software com IA - Full Cycle.

---

## 📧 Suporte

Para dúvidas ou problemas:
- Consulte a documentação do [LangChain](https://python.langchain.com/)
- Veja os [requirements](Requirements.md) originais do projeto
- Abra uma issue no repositório