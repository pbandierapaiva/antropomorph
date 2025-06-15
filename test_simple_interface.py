#!/usr/bin/env python3
"""
Teste simplificado para verificar se a interface web está funcionando
"""

import requests
import json

def test_api_directly():
    """Testa a API diretamente"""
    print("=== Testando API diretamente ===")
    
    data = {
        'nome': 'Maria Silva',
        'data_nascimento': '2015-06-15',
        'data_avaliacao': '2024-01-15',
        'sexo': 'F',
        'peso_kg': 18.5,
        'altura_cm': 110.0
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/processar/individual', json=data)
        result = response.json()
        print(f"Status: {response.status_code}")
        print("Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"Erro na API: {e}")
        return None

def test_web_pages():
    """Testa se as páginas web estão carregando"""
    print("\n=== Testando Páginas Web ===")
    
    try:
        # Testa se a página principal carrega
        response = requests.get('http://localhost:8000')
        print(f"Página principal - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Página principal carregou com sucesso")
            
            # Verifica se contém elementos esperados
            html_content = response.text
            checks = [
                ('individualForm' in html_content, 'Formulário individual'),
                ('script.js' in html_content, 'Arquivo JavaScript'),
                ('style.css' in html_content, 'Arquivo CSS'),
                ('processar/individual' in html_content, 'Endpoint da API')
            ]
            
            for check, description in checks:
                print(f"{'✓' if check else '✗'} {description}: {'Encontrado' if check else 'Não encontrado'}")
            
            # Verifica se os arquivos estáticos estão sendo servidos
            css_response = requests.get('http://localhost:8000/static/css/style.css')
            js_response = requests.get('http://localhost:8000/static/js/script.js')
            
            print(f"{'✓' if css_response.status_code == 200 else '✗'} CSS - Status: {css_response.status_code}")
            print(f"{'✓' if js_response.status_code == 200 else '✗'} JS - Status: {js_response.status_code}")
            
            return True
        else:
            print(f"✗ Erro ao carregar página principal: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erro no teste de páginas: {e}")
        return False

def test_specific_data():
    """Testa com dados específicos que podem causar problemas"""
    print("\n=== Testando Dados Específicos ===")
    
    test_cases = [
        {
            'nome': 'Teste Sem Nome',
            'nome': None,  # Sobrescreve o anterior
            'data_nascimento': '2010-01-15',
            'data_avaliacao': '2024-01-15',
            'sexo': 'M',
            'peso_kg': 30.5,
            'altura_cm': 140.2
        },
        {
            'nome': 'João da Silva',
            'data_nascimento': '2020-01-01',
            'data_avaliacao': '2024-01-15',
            'sexo': 'M',
            'peso_kg': 15.0,
            'altura_cm': 95.0
        }
    ]
    
    for i, data in enumerate(test_cases, 1):
        print(f"\nTeste {i}:")
        try:
            response = requests.post('http://127.0.0.1:8000/api/processar/individual', json=data)
            result = response.json()
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ Nome: {result.get('nome', 'N/A')}")
                print(f"  ✓ IMC: {result.get('imc', 'N/A')}")
                print(f"  ✓ Indicadores: {len(result.get('indicadores', []))}")
            else:
                print(f"  ✗ Erro: {result.get('detail', 'Erro desconhecido')}")
        except Exception as e:
            print(f"  ✗ Exceção: {e}")

if __name__ == "__main__":
    print("Iniciando testes da interface...")
    
    # Teste da API
    api_result = test_api_directly()
    
    # Teste das páginas web
    web_result = test_web_pages()
    
    # Teste com dados específicos
    test_specific_data()
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"{'✓' if api_result else '✗'} API funcionando")
    print(f"{'✓' if web_result else '✗'} Páginas web carregando")
    
    if api_result and web_result:
        print("\n🎉 O sistema está funcionando corretamente!")
        print("\n📝 INSTRUÇÕES PARA TESTAR NO NAVEGADOR:")
        print("1. Abra http://localhost:8000 no seu navegador")
        print("2. Preencha o formulário com dados de teste:")
        print("   - Nome: João Silva")
        print("   - Data de nascimento: 2010-01-15")
        print("   - Data de avaliação: 2024-01-15")
        print("   - Sexo: M")
        print("   - Peso: 30.5")
        print("   - Altura: 140.2")
        print("3. Clique em 'Processar'")
        print("4. Verifique se os resultados aparecem na tabela")
        print("\n💡 Se houver erros no navegador:")
        print("- Abra as Ferramentas de Desenvolvedor (F12)")
        print("- Vá na aba Console para ver erros JavaScript")
        print("- Recarregue a página com Ctrl+F5")
    else:
        print("\n❌ Há problemas que precisam ser corrigidos.")
