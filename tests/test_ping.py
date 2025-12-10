from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_ping():
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_gps_distance_trivial_same_cep():
    payload = {"cep_origem": "1000-001", "cep_destino": "1000-001", "vehicle_type": "ligeiro"}
    r = client.post("/gps/distance", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("distance") == 0.0
    assert body.get("source") == "trivial"
