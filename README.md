# API_GPS

Pequeno serviço HTTP em FastAPI para calcular distâncias/tempos entre dois CEPs (Portugal), usando scraping de `codigo-postal.pt` e o serviço TomTom.

## Execução local (PowerShell)

Instalar dependências:

```powershell
pip install -r requirements.txt
```

Executar a API:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

Healthcheck:

```powershell
Invoke-WebRequest http://127.0.0.1:8010/ping | Select-Object -ExpandProperty Content
```

Exemplo de pedido POST (PowerShell):

```powershell
$body = @{ cep_origem = '1000-001'; cep_destino = '1000-002'; vehicle_type = 'ligeiro' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8010/gps/distance -Body $body -ContentType 'application/json'
```

Nota: este serviço espera uma variável de ambiente `TOMTOM_API_KEY` configurada se quiser usar a API do TomTom.

## Estrutura
- `main.py` — entrypoint e lógica principal
- `requirements.txt` — dependências
- `.github/copilot-instructions.md` — instruções para agentes AI

## Próximos passos recomendados
- Adicionar `requirements-dev.txt` com `pytest` e `httpx` e criar testes básicos.
- Adicionar `Dockerfile` e workflow CI para correr testes.

## Integração contínua (GitHub Actions)

Existe um workflow de CI incluído em `.github/workflows/ci.yml` que é acionado em `push` e `pull_request` para as branches `main` e `master`.

O que faz:
- Faz checkout do código.
- Configura Python (versão 3.12).
- Instala dependências de runtime (`requirements.txt`) e, se existir, dependências de desenvolvimento (`requirements-dev.txt`).
- Executa os testes com `pytest`.

Como ler os resultados:
- Após abrir um Pull Request ou fazer push, aceda à aba `Actions` do repositório ou ao check do Pull Request.
- Clique no workflow `CI` e depois na execução específica para ver logs das etapas (checkout, instalação, execução dos testes).
- O passo `Run tests` falhará se algum teste não passar; o log mostra a saída completa do `pytest`.

Executar localmente (simular CI):

```powershell
# activar venv e instalar deps dev
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

Se quiseres simular o workflow no teu PC (não obrigatório), podes usar a ferramenta `act` (https://github.com/nektos/act) para executar GitHub Actions localmente.


## Ambiente de desenvolvimento (venv) e testes

Para trabalhar localmente e correr testes, recomenda-se usar um ambiente virtual Python.

PowerShell — criar e activar um venv e instalar dependências:

```powershell
# criar venv
python -m venv .venv

# activar venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# instalar dependências de runtime
pip install -r requirements.txt

# instalar dependências de desenvolvimento (tests)
pip install -r requirements-dev.txt

# correr testes
pytest -q
```

Se preferir usar o Python do venv directamente:

```powershell
C:/Ferramentas/API_GPS/.venv/Scripts/python.exe -m pytest -q
```

Isto garante que as bibliotecas de teste (`pytest`, `httpx`, ...) são isoladas do sistema.
