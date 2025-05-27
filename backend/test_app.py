from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome" in r.json()["msg"]

def test_ask_leave_fulltime():
    r = client.get("/ask", params={"question": "How much annual leave do I get?", "role": "full-time"})
    assert r.status_code == 200
    assert "20 days" in r.json().get("answer", "")

def test_ask_leave_contractor():
    r = client.get("/ask", params={"question": "Do I get annual leave?", "role": "contractor"})
    assert r.status_code == 200
    assert "not entitled" in r.json().get("answer", "")

def test_ask_overtime_employee():
    r = client.get("/ask", params={"question": "What about overtime pay?", "role": "employee"})
    assert r.status_code == 200
    assert "overtime" in r.json().get("answer", "").lower()
