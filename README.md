# API_GPS

Serviço FastAPI para calcular distâncias e tempos entre dois Códigos Postais (CEP) em Portugal, integrando scraping de `codigo-postal.pt` e cálculos de rota via TomTom. Pode ser executado como serviço Windows (NSSM) ou em containerização Docker.

## 📋 Funcionalidades

- ✅ Endpoint `/ping` para verificação de saúde da API
- ✅ Endpoint `/gps/distance` para cálculo de distância/tempo entre dois CEPs
- ✅ Suporte a múltiplos tipos de veículos (ligeiro, pesado, van, truck)
- ✅ Cache em memória (rápido) e cache persistente em SQLite
- ✅ Integração com SAP via HTTP POST (JSON)
- ✅ Logging estruturado para debug e monitorização
- ✅ Testes automáticos e CI/CD com GitHub Actions

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

## Integração com SAP (SM59)

A API pode ser consumida diretamente pelo SAP R/3 ou S/4HANA através de um HTTP Destination (SM59).

### Configurar SM59 no SAP

| Campo | Valor |
|-------|-------|
| Tipo | G (HTTP) |
| Host | IP/hostname da máquina com a API |
| Porta | 8010 |
| Path Prefix | `/` |

### Exemplo de Chamada ABAP

```abap
DATA: lo_client    TYPE REF TO if_http_client,
      lv_body      TYPE string,
      lv_response  TYPE string.

CONCATENATE
  '{"cep_origem":"1000-001",'
  '"cep_destino":"1000-002",'
  '"vehicle_type":"truck"}'
INTO lv_body.

cl_http_client=>create_by_destination(
  EXPORTING destination = 'Z_API_GPS'
  IMPORTING client = lo_client
).

lo_client->request->set_method( 'POST' ).
lo_client->request->set_header_field( name = 'Content-Type' value = 'application/json' ).
lo_client->request->set_header_field( name = '~request_uri' value = '/gps/distance' ).
lo_client->request->set_cdata( lv_body ).
lo_client->send( ).
lo_client->receive( ).

lv_response = lo_client->response->get_cdata( ).
WRITE: / lv_response.
```

## Deploy em Servidor Windows (com NSSM)

Para executar como serviço Windows permanente:

1. Instalar NSSM: https://nssm.cc/download
2. Criar serviço:
   ```powershell
   nssm install API_GPS_DISTANCE
   ```
3. Configurar:
   - Application Path: `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe`
   - Startup Directory: `C:\Ferramentas\API_GPS`
   - Arguments: `-m uvicorn main:app --host 0.0.0.0 --port 8010`
4. Iniciar: `nssm start API_GPS_DISTANCE`
5. Abrir firewall:
   ```powershell
   New-NetFirewallRule -DisplayName "API_GPS_8010" -Direction Inbound -Protocol TCP -LocalPort 8010 -Action Allow
   ```

## Variáveis de Ambiente

Configure `TOMTOM_API_KEY` para usar a API do TomTom:

```powershell
$env:TOMTOM_API_KEY = "sua_chave_aqui"
```

Ou copie `env.sample` para `config.env` local (não commita segredos):

```powershell
Copy-Item env.sample config.env
# Editar config.env e adicionar a chave real
```

## Swagger UI (Documentação Interativa)

Aceda a `http://localhost:8010/docs` para explorar a API interactivamente.
