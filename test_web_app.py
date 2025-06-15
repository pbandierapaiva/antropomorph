import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_homepage_loads():
    """Testa se a página principal carrega sem erros"""
    client = TestClient(app)
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Página principal carregou com sucesso!")
        print("✅ Aplicação está funcionando!")
    else:
        print(f"❌ Erro na página: {response.status_code}")
        print(f"Conteúdo: {response.text[:500]}")
    
    assert response.status_code == 200

if __name__ == "__main__":
    test_homepage_loads()
