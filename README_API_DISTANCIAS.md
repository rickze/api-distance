
# API de Distâncias – Integração SAP + FastAPI

Este repositório contém a API utilizada para cálculo de distâncias e tempos entre dois Códigos Postais (CEP), com integração direta ao SAP R/3 através de chamadas HTTP.  
A API utiliza FastAPI, Python e Uvicorn, podendo ser executada como serviço Windows através do NSSM.

---

## 🚀 Funcionalidades

- Cálculo de distâncias entre dois CEPs
- Estimativa de tempo prevista com base no tipo de veículo
- Suporte a POST (SAP) e GET (browser/Postman)
- API executada como serviço do Windows (NSSM)
- Integração ABAP estável com tratamento de erros
- Cache automática no SAP (tabela ZFI_CEP_DISTANCE)

---

## 📂 Estrutura do Projeto

```
main.py
requirements.txt
```

Endpoints principais:

### 🔹 Verificar se a API está ativa
```
GET /ping
```

Resposta:
```json
{"status": "ok"}
```

### 🔹 Cálculo por CEP
```
POST /gps/distance
```

Body JSON:
```json
{
  "cep_origem": "4700-394",
  "cep_destino": "4650-361",
  "vehicle_type": "truck"
}
```

Resposta:
```json
{
  "origin_cep": "4700-394",
  "destination_cep": "4650-361",
  "vehicle_type": "truck",
  "tomtom_travel_mode": "truck",
  "distance": 46.35,
  "distance_unit": "km",
  "travel_time": 35.55,
  "time_unit": "min"
}
```

---

## 🛠 Requisitos

### ✔ Python 3.12+
Download:  
https://www.python.org/downloads/

Instalar dependências:
```
pip install -r requirements.txt
```

Dependências:
```
fastapi
uvicorn
requests
pandas
```

---

## ⚙ Execução Local

```
python -m uvicorn main:app --host 0.0.0.0 --port 8010
```

Testar no browser:
```
http://localhost:8010/ping
```

---

## 🧱 Deploy da API no Servidor Windows

### ✔ 1. Criar diretório da API
```
C:\APIs\GPS_DISTANCE```

### ✔ 2. Copiar os ficheiros
```
main.py
requirements.txt
```

### ✔ 3. Instalar dependências
```
pip install -r requirements.txt
```

### ✔ 4. Instalar NSSM  
Download: https://nssm.cc/download

Criar serviço:
```
nssm install API_GPS_DISTANCE
```

Parâmetros:
- Path: `C:\Python312\python.exe`
- Startup directory: `C:\APIs\GPS_DISTANCE`
- Arguments:
```
-m uvicorn main:app --host 0.0.0.0 --port 8010
```

Iniciar serviço:
```
nssm start API_GPS_DISTANCE
```

---

## 🔥 Integração SAP

### Configurar a Destination HTTP (SM59)

| Campo | Valor |
|------|--------|
| Tipo | G (HTTP) |
| Host | IP do servidor |
| Porta | 8010 |
| Path Prefix | /ping |

A função SAP usa:
```
~request_uri = '/gps/distance'
```

---

## 🔷 Função SAP recomendada: ZFI_CEP_DISTANCE_GET

A função realiza:

1. Leitura da tabela ZFI_CEP_DISTANCE (cache)
2. Chamada HTTP à API
3. Tratamento de erros SEND/RECEIVE
4. Interpretação do JSON
5. Atualização da cache
6. Retorno dos valores ao ABAP

Campos devolvidos:

- Distância (km)
- Unidade (KM)
- Tempo (min)
- Unidade (MIN)
- Status HTTP
- Mensagem de erro (se existir)

---

## 🧪 Teste via Postman

POST:
```
http://<SERVER_IP>:8010/gps/distance
```

Body:
```json
{
  "cep_origem": "4700-394",
  "cep_destino": "4650-361",
  "vehicle_type": "truck"
}
```

---

## 🛡 Troubleshooting

### ❗ API não arranca como serviço
```
nssm status API_GPS_DISTANCE
```

### ❗ SAP devolve HTTP 404
Destino SM59 configurado incorretamente.

### ❗ HTTP_COMMUNICATION_FAILURE no SAP
API está desligada / firewall bloqueia porta 8010.

### ❗ Teste rápido
```
http://<IP>:8010/ping
```

---

## 📜 Licença
Uso interno.

---

## 👤 Autor
Desenvolvido para integração corporativa SAP.

---

