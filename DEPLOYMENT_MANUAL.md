# 🚀 Manual de Deploy - API_GPS no Servidor Interno (Windows)

**Objetivo:** Instalar e configurar a API_GPS como serviço Windows permanente, integrado com SAP.

**Ambiente alvo:** Windows Server 2019/2022 ou Windows 10/11 Pro (com permissões administrativas).

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Fase 1: Instalação de Python](#fase-1-instalação-de-python)
3. [Fase 2: Preparação do Projeto](#fase-2-preparação-do-projeto)
4. [Fase 3: Configuração de Variáveis de Ambiente](#fase-3-configuração-de-variáveis-de-ambiente)
5. [Fase 4: Instalação e Configuração de NSSM](#fase-4-instalação-e-configuração-de-nssm)
6. [Fase 5: Criação do Serviço Windows](#fase-5-criação-do-serviço-windows)
7. [Fase 6: Configuração de Firewall](#fase-6-configuração-de-firewall)
8. [Fase 7: Integração SAP (SM59)](#fase-7-integração-sap-sm59)
9. [Fase 8: Testes e Validação](#fase-8-testes-e-validação)
10. [Troubleshooting](#troubleshooting)
11. [Manutenção e Monitorização](#manutenção-e-monitorização)

---

## ⚙️ Pré-requisitos

- ✅ Acesso administrativo ao servidor Windows
- ✅ Ligação à internet (para download de Python, NSSM, dependências)
- ✅ Repositório Git clonado ou ficheiros do projeto disponíveis
- ✅ Chave da API TomTom (obtida em https://developer.tomtom.com)
- ✅ Acesso ao SAP para configuração SM59

---

## Fase 1: Instalação de Python

### Passo 1.1: Download do Python

1. Acede a https://www.python.org/downloads/
2. **Descarrega Python 3.12.x** (versão recente e estável)
3. Escolhe o instalador executável para Windows (x86-64 bit recomendado)

### Passo 1.2: Instalar Python

1. Executa o instalador como Administrador
2. **IMPORTANTE:** Na primeira janela, marca:
   - ✅ "Add Python to PATH"
   - ✅ "Install for all users"
3. Clica em "Customize installation"
4. Marca todas as opções (pip, tcl/tk, etc.)
5. Na próxima janela, marca "Install for all users" e escolhe pasta de instalação:
   ```
   C:\Python312
   ```
6. Clica em "Install"

### Passo 1.3: Verificar Instalação

Abre PowerShell como Administrador e executa:

```powershell
python --version
pip --version
```

Deverá aparecer:
```
Python 3.12.x
pip 24.x.x
```

---

## Fase 2: Preparação do Projeto

### Passo 2.1: Criar Diretório da API

Criar o diretório base onde a API ficará instalada:

```powershell
New-Item -ItemType Directory -Path "C:\APIs\GPS_DISTANCE" -Force
```

---

### Passo 2.2: Copiar Ficheiros do Projeto

Copiar todos os ficheiros do repositório para:

```
C:\APIs\GPS_DISTANCE\
```

Estrutura recomendada:

```
C:\APIs\GPS_DISTANCE\
├── main.py
├── inspect_cache.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── .gitignore
├── env.sample
└── tests\
    └── test_ping.py
```

---

### Passo 2.3: Configuração da Execution Policy do PowerShell

Para ativar o ambiente virtual Python (`.\venv\Scripts\Activate.ps1`), é necessário garantir que o PowerShell permite a execução de scripts locais.

Caso contrário, poderá surgir o erro:

> running scripts is disabled on this system.

#### 2.3.1 Verificar a Execution Policy atual

```powershell
Get-ExecutionPolicy -List
```

#### 2.3.2 Opção recomendada (por utilizador): RemoteSigned

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Permite scripts locais mas mantém segurança para scripts da internet.

#### 2.3.3 Opção temporária (válida apenas para a sessão atual)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Não altera a configuração do sistema — ideal para testes rápidos.

#### 2.3.4 Opção global (não recomendada)

```powershell
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned
```

Aplicar apenas em ambientes controlados e com aprovação da equipa de segurança.

---

### Passo 2.4: Criar Ambiente Virtual e Instalar Dependências

> ⚠ **Executar em PowerShell como Administrador**

```powershell
cd C:\APIs\GPS_DISTANCE

# Criar virtual environment (opcional mas recomendado)
python -m venv venv

# Activar venv
.\venv\Scripts\Activate.ps1

# Instalar dependências de runtime
pip install -r requirements.txt
```

**Dependências instaladas:**
- fastapi
- uvicorn
- requests

(O ficheiro `requirements-dev.txt` contém dependências para testes e desenvolvimento.)

---

### Passo 2.5: Teste Rápido da API (Opcional)

Com o ambiente virtual ativado:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8010
```

Noutro PowerShell, testar o endpoint de saúde:

```powershell
Invoke-WebRequest http://127.0.0.1:8010/ping
```

Resposta esperada:

```json
{"status": "ok"}
```

Parar o servidor com:

```
Ctrl + C
```

---

## Fase 3: Configuração de Variáveis de Ambiente

### Passo 3.1: Criar Ficheiro `config.env` Local

Na pasta `C:\APIs\GPS_DISTANCE`, cria um ficheiro `config.env`:

```powershell
# Abre editor de texto (Notepad)
notepad C:\APIs\GPS_DISTANCE\config.env
```

Adiciona o seguinte conteúdo:

```env
TOMTOM_API_KEY=TUA_CHAVE_TOMTOM_AQUI
```

**Substitui `TUA_CHAVE_TOMTOM_AQUI` pela tua chave real** (obtida em https://developer.tomtom.com).

Guarda o ficheiro.

### Passo 3.2: Definir Variável de Ambiente do Sistema (Windows)

#### Opção A: Via PowerShell (Administrador)

```powershell
# Define variável de ambiente para o utilizador actual
[Environment]::SetEnvironmentVariable("TOMTOM_API_KEY", "TUA_CHAVE_AQUI", "User")

# Define variável de ambiente para todo o sistema (requer Admin)
[Environment]::SetEnvironmentVariable("TOMTOM_API_KEY", "TUA_CHAVE_AQUI", "Machine")
```

#### Opção B: Via Interface Gráfica

1. Abre "Editar as variáveis de ambiente do sistema":
   - Procura por "environment" no menu Iniciar
   - Clica em "Edit environment variables for your account" ou "Edit the system environment variables"

2. Clica em "Environment Variables..."

3. Na secção "User variables" ou "System variables", clica em "New..."

4. Adiciona:
   - **Variable name:** `TOMTOM_API_KEY`
   - **Variable value:** `TUA_CHAVE_AQUI`

5. Clica em "OK" e fecha as janelas.

6. **Reinicia o computador** ou o PowerShell para as alterações surtirem efeito.

### Passo 3.3: Verificar Variável de Ambiente

Abre um novo PowerShell como Administrador e executa:

```powershell
$env:TOMTOM_API_KEY
```

Deverá aparecer a tua chave.

---

## Fase 4: Instalação e Configuração de NSSM

### Passo 4.1: Download e Instalação do NSSM

1. Acede a https://nssm.cc/download
2. Descarrega o ficheiro ZIP (versão 2.24 ou mais recente)
3. Extrai para uma pasta temporária:
   ```powershell
   Expand-Archive -Path "$env:USERPROFILE\Downloads\nssm-2.24-101-g897c7ad.zip" -DestinationPath "$env:USERPROFILE\Downloads"
   ```

4. Copia o executável para `System32`:
   ```powershell
   # Para Windows 64-bit:
   Copy-Item "$env:USERPROFILE\Downloads\nssm-2.24-101-g897c7ad\win64\nssm.exe" -Destination "C:\Windows\System32\" -Force

   # Para Windows 32-bit:
   # Copy-Item "$env:USERPROFILE\Downloads\nssm-2.24-101-g897c7ad\win32\nssm.exe" -Destination "C:\Windows\System32\" -Force
   ```

### Passo 4.2: Verificar Instalação do NSSM

```powershell
nssm version
```

Deverá aparecer:
```
nssm 2.24 (...)
```

---

## Fase 5: Criação do Serviço Windows

### Passo 5.1: Instalar o Serviço com NSSM

Abre PowerShell como Administrador e executa:

```powershell
nssm install API_GPS_Distance
```

Abre-se uma janela de configuração. Preenche os campos:

| Campo | Valor |
|-------|-------|
| **Path** | `C:\Python312\python.exe` (ou o caminho da tua instalação Python) |
| **Startup directory** | `C:\APIs\GPS_DISTANCE` |
| **Arguments** | `-m uvicorn main:app --host 0.0.0.0 --port 8010` |
| **Service name** | `API_GPS_Distance` |

Depois clica em "Install service".

### Passo 5.2: Configurar Conta de Utilizador do Serviço

1. Abre "Services" (services.msc):
   ```powershell
   services.msc
   ```

2. Procura por "API_GPS_Distance"

3. Clica com botão direito → "Properties"

4. Vai ao separador "Log On"

5. Escolhe uma das opções:
   - **Local System account** — mais fácil mas menos seguro
   - **This account** — mais seguro (especifica utilizador com permissões de rede)

6. Clica em "Apply" e depois "OK"

### Passo 5.3: Configurar Reinício Automático do Serviço

1. Em "Services", procura "API_GPS_Distance"
2. Clica com botão direito → "Properties"
3. Vai ao separador "Recovery"
4. Em "First failure", "Second failure" e "Subsequent failures", escolhe "Restart the service"
5. Define tempo de restart (ex: 10 segundos)
6. Clica "OK"

---

## Fase 6: Configuração de Firewall

### Passo 6.1: Abrir Porta 8010 na Firewall

Abre PowerShell como Administrador e executa:

```powershell
# Criar regra de entrada (inbound)
New-NetFirewallRule `
  -DisplayName "API_GPS_Distance_Inbound" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8010 `
  -Action Allow

# Criar regra de saída (outbound) — opcional
New-NetFirewallRule `
  -DisplayName "API_GPS_Distance_Outbound" `
  -Direction Outbound `
  -Protocol TCP `
  -RemotePort 443 `
  -Action Allow
```

### Passo 6.2: Verificar Regras

```powershell
Get-NetFirewallRule -DisplayName "API_GPS_Distance*" | Format-Table
```

---

## Fase 7: Iniciar o Serviço

### Passo 7.1: Iniciar o Serviço

Abre PowerShell como Administrador e executa:

```powershell
# Iniciar serviço
Start-Service -Name "API_GPS_Distance"

# Verificar estado
Get-Service -Name "API_GPS_Distance"

# Ver logs (opcional)
Get-EventLog -LogName System -Source nssm -Newest 5 | Format-List
```

### Passo 7.2: Verificar se Está a Ouvir na Porta 8010

```powershell
netstat -ano | findstr ":8010"
```

Deverá aparecer uma linha com LISTENING.

---

## Fase 8: Testes e Validação

### Passo 8.1: Teste de Healthcheck Local

```powershell
Invoke-WebRequest http://localhost:8010/ping | Select-Object -ExpandProperty Content
```

Deverá retornar:
```json
{"status":"ok"}
```

### Passo 8.2: Teste de Healthcheck Remoto

De outro computador na rede, testa:

```powershell
$ip = "192.168.x.x"  # Substitui pelo IP do servidor
Invoke-WebRequest "http://$ip:8010/ping" | Select-Object -ExpandProperty Content
```

### Passo 8.3: Teste de Distância (Trivial)

```powershell
$body = @{
    cep_origem = "1000-001"
    cep_destino = "1000-001"
    vehicle_type = "ligeiro"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8010/gps/distance" `
  -Body $body `
  -ContentType "application/json"
```

Deverá retornar:
```json
{
  "origin_cep": "1000-001",
  "destination_cep": "1000-001",
  "distance": 0.0,
  "source": "trivial"
}
```

### Passo 8.4: Swagger UI (Documentação Interativa)

Acede a:
```
http://localhost:8010/docs
```

Podes explorar e testar os endpoints interactivamente.

---

## Fase 9: Integração SAP (SM59)

### Passo 9.1: Configurar HTTP Destination no SAP

1. Abre transação **SM59** no SAP
2. Clica em "Create" (ou edita uma existente)
3. Define:
   - **Destination name:** `Z_API_GPS_DISTANCE`
   - **Destination type:** `G (HTTP)`
   - **Technical settings:**
     - **Host:** IP do servidor Windows (ex: `192.168.1.100`)
     - **Port:** `8010`
     - **Path prefix:** `/`
   - **Logon & Security:**
     - **Authentication:** `Basic` (se necessário)

4. Clica em "Save"

### Passo 9.2: Testar Destination no SAP

1. Selecciona a destination `Z_API_GPS_DISTANCE`
2. Clica em "Test Connection" ou "Connection Test"
3. Deverá retornar sucesso

### Passo 9.3: Criar Função ABAP para Chamar API

Cria uma função RFC (ex: `ZFI_CEP_DISTANCE_GET`) que chama a API:

```abap
FUNCTION zfi_cep_distance_get.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(P_CEP_ORIGEM) TYPE STRING
*"     VALUE(P_CEP_DESTINO) TYPE STRING
*"     VALUE(P_VEHICLE_TYPE) TYPE STRING DEFAULT 'truck'
*"  EXPORTING
*"     VALUE(P_DISTANCE) TYPE P
*"     VALUE(P_TIME) TYPE P
*"     VALUE(P_STATUS) TYPE I
*"     VALUE(P_MESSAGE) TYPE STRING
*"----------------------------------------------------------------------

  DATA: lo_client    TYPE REF TO if_http_client,
        lv_body      TYPE string,
        lv_response  TYPE string,
        lv_json_resp TYPE string.

  TRY.
    " Construir JSON de entrada
    CONCATENATE
      '{"cep_origem":"' p_cep_origem '",'
      '"cep_destino":"' p_cep_destino '",'
      '"vehicle_type":"' p_vehicle_type '"}'
      INTO lv_body.

    " Criar cliente HTTP
    cl_http_client=>create_by_destination(
      EXPORTING
        destination = 'Z_API_GPS_DISTANCE'
      IMPORTING
        client = lo_client
      EXCEPTIONS
        others = 1
    ).

    IF sy-subrc <> 0.
      p_status = sy-subrc.
      p_message = 'Erro ao criar cliente HTTP'.
      EXIT.
    ENDIF.

    " Configurar pedido
    lo_client->request->set_method( 'POST' ).
    lo_client->request->set_header_field(
      name = 'Content-Type'
      value = 'application/json'
    ).
    lo_client->request->set_header_field(
      name = '~request_uri'
      value = '/gps/distance'
    ).
    lo_client->request->set_cdata( lv_body ).

    " Enviar pedido
    lo_client->send(
      EXCEPTIONS
        others = 1
    ).

    IF sy-subrc <> 0.
      p_status = sy-subrc.
      p_message = 'Erro ao enviar pedido HTTP'.
      EXIT.
    ENDIF.

    " Receber resposta
    lo_client->receive(
      EXCEPTIONS
        others = 1
    ).

    IF sy-subrc <> 0.
      p_status = sy-subrc.
      p_message = 'Erro ao receber resposta HTTP'.
      EXIT.
    ENDIF.

    " Obter dados da resposta
    lv_response = lo_client->response->get_cdata( ).
    p_status = lo_client->response->get_status( ).
    p_message = lv_response.

    " Parse JSON (simplificado — considera usar biblioteca JSON)
    " Exemplo: extrai "distance" e "travel_time"
    IF p_status = 200.
      " TODO: fazer parsing JSON da resposta
      " P_DISTANCE = ...
      " P_TIME = ...
    ELSE.
      p_message = 'Erro na API: ' && lv_response.
    ENDIF.

  CATCH cx_root INTO DATA(ex).
    p_status = 1.
    p_message = ex->get_text( ).
  ENDTRY.

ENDFUNCTION.
```

### Passo 9.4: Testar Função no SAP

1. Abre transação **SE37**
2. Procura por `ZFI_CEP_DISTANCE_GET`
3. Clica em "Test"
4. Preenche os parâmetros:
   - `P_CEP_ORIGEM` = `1000-001`
   - `P_CEP_DESTINO` = `1000-002`
   - `P_VEHICLE_TYPE` = `truck`
5. Executa e valida a resposta

---

## Fase 10: Troubleshooting

### Problema: Serviço não inicia

**Sinal:** Erro ao tentar `Start-Service -Name "API_GPS_Distance"`

**Solução:**
1. Verifica logs:
   ```powershell
   Get-EventLog -LogName System -Source nssm -Newest 10 | Format-List
   ```
2. Verifica caminho do Python:
   ```powershell
   "C:\Python312\python.exe" -c "print('OK')"
   ```
3. Verifica se `main.py` tem erros:
   ```powershell
   cd C:\APIs\GPS_DISTANCE
   python main.py
   ```

### Problema: Porta 8010 já em uso

**Sinal:** `Address already in use`

**Solução:**
```powershell
# Encontra processo na porta 8010
netstat -ano | findstr ":8010"

# Mata o processo (substitui PID)
taskkill /PID <PID> /F

# Ou muda porta em main.py e NSSM
```

### Problema: Variável de ambiente não encontrada

**Sinal:** `RuntimeError: TomTom API key not configured`

**Solução:**
1. Verifica se variável está definida:
   ```powershell
   $env:TOMTOM_API_KEY
   ```
2. Se vazia, define:
   ```powershell
   [Environment]::SetEnvironmentVariable("TOMTOM_API_KEY", "CHAVE", "Machine")
   ```
3. **Reinicia o serviço:**
   ```powershell
   Restart-Service -Name "API_GPS_Distance"
   ```

### Problema: Firewall bloqueia ligações

**Sinal:** Timeout em tentativas de ligação remota

**Solução:**
```powershell
# Verifica regra
Get-NetFirewallRule -DisplayName "*API_GPS*"

# Remove e recria
Remove-NetFirewallRule -DisplayName "API_GPS_Distance_Inbound" -Confirm:$false
New-NetFirewallRule -DisplayName "API_GPS_Distance_Inbound" `
  -Direction Inbound -Protocol TCP -LocalPort 8010 -Action Allow
```

---

## Fase 11: Manutenção e Monitorização

### Monitorização Diária

```powershell
# Verificar estado do serviço
Get-Service -Name "API_GPS_Distance" | Format-List

# Ver últimos logs
Get-EventLog -LogName System -Source nssm -Newest 5 | Format-List

# Testar healthcheck
Invoke-WebRequest http://localhost:8010/ping
```

### Reiniciar Serviço (se necessário)

```powershell
Restart-Service -Name "API_GPS_Distance"
```

### Parar Serviço (para manutenção)

```powershell
Stop-Service -Name "API_GPS_Distance"
```

### Atualizar Código

1. Pára o serviço:
   ```powershell
   Stop-Service -Name "API_GPS_Distance"
   ```

2. Substitui ficheiros em `C:\APIs\GPS_DISTANCE`

3. Reinicia:
   ```powershell
   Start-Service -Name "API_GPS_Distance"
   ```

### Logs e Debugging

Ficheiros de log (se configurado):
```
C:\APIs\GPS_DISTANCE\logs\
```

Ver logs do Windows:
```powershell
# Event Viewer
eventvwr.msc

# Ou PowerShell
Get-EventLog -LogName Application -Source "uvicorn" -Newest 20
```

---

## 📞 Suporte e Contato

Se encontrares problemas:

1. **Verifica os logs** (`Get-EventLog` ou Event Viewer)
2. **Testa manualmente:**
   ```powershell
   cd C:\APIs\GPS_DISTANCE
   python main.py
   ```
3. **Consulta a documentação do repositório:** https://github.com/rickze/api-distance

---

## ✅ Checklist Final

- [ ] Python 3.12+ instalado e PATH configurado
- [ ] Projeto clonado em `C:\APIs\GPS_DISTANCE`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Variável `TOMTOM_API_KEY` definida no sistema
- [ ] NSSM instalado e verificado
- [ ] Serviço `API_GPS_Distance` criado com NSSM
- [ ] Porta 8010 aberta na firewall
- [ ] Serviço iniciado e a responder
- [ ] Healthcheck (`/ping`) funciona
- [ ] SM59 configurado no SAP
- [ ] Teste funcional SAP ↔ API bem-sucedido
- [ ] Logs a ser registados adequadamente
- [ ] Plano de backup e recuperação em lugar

---

**Documento criado em:** 10 de Dezembro de 2025  
**Versão:** 1.0  
**Status:** Pronto para Produção
