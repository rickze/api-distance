# Instruções Copilot / Agente AI (específicas do projeto)

Este repositório é um serviço FastAPI minimalista. Estas instruções ajudam agentes AI a serem produtivos de imediato, descrevendo estrutura, convenções e comandos de execução/depuração.

**Visão Geral**
- **Tipo de repo:** serviço HTTP FastAPI de ficheiro único
- **Ficheiros chave:** `main.py` (entrypoint da aplicação), `requirements.txt` (dependências)
- **Como executar:** `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

**Arquitetura e Padrões**
- **Aplicação FastAPI única:** a instância `app` de FastAPI é criada em `main.py`. Endpoints usam decoradores (`@app.get`, `@app.post`, ...).
- **Uso de Pydantic:** `pydantic.BaseModel` está importado em `main.py`. Modelos de pedido/resposta são definidos inline ou em novos módulos quando o projecto crescer.
- **Sem camadas adicionais:** não há routers separados, serviços ou persistência; manter alterações pequenas. Se adicionar separação, crie pastas como `app/`, `routers/`, `models/` e actualize importações.

**Fluxo de trabalho do desenvolvedor (comandos)**
- **Instalar dependências:** `pip install -r requirements.txt`
- **Executar localmente (PowerShell):**
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **Verificação de saúde:** GET `http://127.0.0.1:8000/ping` devolve `{"status":"ok"}`.

**Convenções específicas do projecto**
- **Nome do entrypoint:** mantenha a instância FastAPI chamada `app` em `main.py` para compatibilidade com `uvicorn main:app`.
- **Alterações de pequena escala:** como o projecto é de ficheiro único, prefira alterações cirúrgicas (adicionar endpoints, modelos). Para módulos novos, crie pastas ao nível superior.

**Pontos de integração e dependências**
- **Dependências actuais:** `requirements.txt` contém `fastapi` e `uvicorn`.
- **Integrações externas:** nenhuma presente. Ao adicionar integrações (BD, APIs externas), use variáveis de ambiente (`.env`) e documente em `README.md`.

**Exemplos concretos (editar código)**
- Adicionar GET: use `@app.get("/rota")` em `main.py` e devolva tipos compatíveis com JSON (dicionários ou modelos Pydantic).
- Aceitar JSON: defina um modelo Pydantic e anote o parâmetro do handler: `def criar(item: ItemModel):` onde `ItemModel(BaseModel)`.
- Dependências: só actualize `requirements.txt` quando adicionar bibliotecas de runtime.

**Cuidados a ter**
- Não mude o nome `app` em `main.py` sem actualizar os comandos de execução ou CI.
- Evite adicionar frameworks pesados ou injeção de dependências complexa — mantenha o projecto simples.

**Ficheiros para inspeccionar**
- `main.py` — estilo e configuração dos endpoints.
- `requirements.txt` — dependências a instalar.

Se quiser, posso traduzir exemplos de endpoints (POST com validação), adicionar um `tests/` mínimo com `pytest`+`httpx`, ou criar um `README.md` e `Dockerfile`. Indique o que prefere.
