# API FastAPI para Consumo via SAP (Windows)

## 📌 Descrição
Este projeto implementa uma API FastAPI para cálculo de distância GPS. A API é executada num PC Windows como serviço, acessível via HTTP pela rede interna e consumida diretamente pelo SAP através de um HTTP Destination (SM59).

## 🚀 Funcionalidades
- Endpoint `/ping` para verificação de disponibilidade
- Endpoint `/gps/distance` para cálculo de distância entre dois pontos (Haversine)
- Execução permanente como serviço Windows (via NSSM)
- Acesso externo através da firewall
- Integração direta com SAP R/3 ou S/4HANA via HTTP

## 🧩 1. Requisitos
- Windows 10/11
- Python 3.12+
- Permissões administrativas
- Ligação interna na LAN
- SAP com capacidade de chamadas HTTP (SM59)

## 🧩 2. Estrutura do projeto
```
C:\Ferramentas\API_GPS\
│   main.py
│   requirements.txt
```

## 🧩 3. Instalação

### 3.1 Criar pasta do projeto
```powershell
mkdir C:\Ferramentas\API_GPS
```

### 3.2 Criar o ficheiro `requirements.txt`
```
fastapi
uvicorn
```

### 3.3 Criar o ficheiro `main.py`
```python
from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status":"ok"}

class GPSPoints(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.post("/gps/distance")
def calcular_distancia(pontos: GPSPoints):
    distancia_km = haversine(pontos.lat1, pontos.lon1, pontos.lat2, pontos.lon2)
    return {"distance_km": round(distancia_km, 3)}
```

## 🧩 4. Instalar dependências
```powershell
cd C:\Ferramentas\API_GPS
python -m pip install -r requirements.txt
```

## 🧩 5. Testar a API
```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8010
```
Testar:
```
http://localhost:8010/ping
```

## 🧩 6. Instalar o NSSM (serviço Windows)

### 6.1 Download NSSM
https://nssm.cc/download

Copiar `nssm.exe` →  
```
C:\Windows\System32\
```

Validar:
```powershell
nssm version
```

### 6.2 Criar serviço Windows
```powershell
nssm install API_GPS_DISTANCE
```

Configuração:
- Application Path:  
  `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe`
- Startup Directory:  
  `C:\Ferramentas\API_GPS`
- Arguments:  
  `-m uvicorn main:app --host 0.0.0.0 --port 8010`

### 6.3 Configurar conta
Em `services.msc` → API_GPS_DISTANCE → Log On → This account.

## 🧩 7. Abrir porta na Firewall
```powershell
New-NetFirewallRule -DisplayName "API_GPS_8010_INBOUND" -Direction Inbound -Protocol TCP -LocalPort 8010 -Action Allow
```

## 🧩 8. Validar acesso externo
```
http://<IP_DA_MAQUINA>:8010/ping
```

## 🧩 9. Configurar SAP – SM59
- Transaction: SM59  
- Criar destination tipo G  
- Host: IP da máquina  
- Port: 8010  
- Path Prefix: `/`

## 🧩 10. Chamada ABAP de exemplo
```abap
DATA: lo_client    TYPE REF TO if_http_client,
      lv_body      TYPE string,
      lv_response  TYPE string.

DATA: lv_lat1 TYPE string VALUE '41.0000',
      lv_lon1 TYPE string VALUE '-8.0000',
      lv_lat2 TYPE string VALUE '41.1500',
      lv_lon2 TYPE string VALUE '-8.6100'.

CONCATENATE
  '{"lat1":'  lv_lat1
  ',"lon1":'  lv_lon1
  ',"lat2":'  lv_lat2
  ',"lon2":'  lv_lon2
  '}'
INTO lv_body.

cl_http_client=>create_by_destination(
  EXPORTING
    destination = 'Z_API_GPS'
  IMPORTING
    client      = lo_client
).

lo_client->request->set_method( 'POST' ).
lo_client->request->set_header_field( name = 'Content-Type' value = 'application/json' ).
lo_client->request->set_header_field( name = '~request_uri'  value = '/gps/distance' ).
lo_client->request->set_cdata( lv_body ).

lo_client->send( ).
lo_client->receive( ).

lv_response = lo_client->response->get_cdata( ).

WRITE: / lv_response.
```

## 🧩 11. Resultado esperado
```
{"distance_km": 53.784}
```

## 🧩 12. Swagger UI
```
http://<IP>:8010/docs
```

---