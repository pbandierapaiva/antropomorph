import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Testa se a página principal carrega"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_health_check():
    """Testa um endpoint básico se existir, ou simplesmente confirma que a app carrega"""
    # Testando se pelo menos conseguimos acessar a aplicação
    response = client.get("/")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
