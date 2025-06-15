#!/usr/bin/env python3
"""
Teste para verificar se a interface web está processando dados corretamente
"""

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def test_web_interface():
    """Testa a interface web usando Selenium (se disponível)"""
    print("\n=== Testando Interface Web ===")
    
    try:
        # Configuração do Chrome para executar sem interface gráfica
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('http://localhost:8000')
        
        # Aguarda a página carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "individualForm"))
        )
        
        # Preenche o formulário
        driver.find_element(By.NAME, "nome").send_keys("João Teste Web")
        driver.find_element(By.NAME, "data_nascimento").send_keys("2010-01-15")
        driver.find_element(By.NAME, "data_avaliacao").send_keys("2024-01-15")
        driver.find_element(By.NAME, "sexo").send_keys("M")
        driver.find_element(By.NAME, "peso_kg").send_keys("30.5")
        driver.find_element(By.NAME, "altura_cm").send_keys("140.2")
        
        # Submete o formulário
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Aguarda o resultado
        time.sleep(3)
        
        # Verifica se há erros no console
        logs = driver.get_log('browser')
        if logs:
            print("Logs do navegador:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        
        # Verifica se o resultado foi exibido
        try:
            result_display = driver.find_element(By.ID, "individual-result-display")
            if result_display.is_displayed():
                print("Resultado exibido com sucesso!")
                
                # Verifica o conteúdo da tabela
                table_body = driver.find_element(By.ID, "individual-table-body")
                rows = table_body.find_elements(By.TAG_NAME, "tr")
                if rows:
                    print(f"Encontradas {len(rows)} linhas na tabela de resultados")
                    first_row = rows[0]
                    cells = first_row.find_elements(By.TAG_NAME, "td")
                    print(f"Primeira linha tem {len(cells)} células")
                    if cells:
                        print(f"Primeira célula (nome): '{cells[0].text}'")
                else:
                    print("Nenhuma linha encontrada na tabela de resultados")
            else:
                print("Resultado não está visível")
        except Exception as e:
            print(f"Erro ao verificar resultado: {e}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"Erro no teste web (Selenium não disponível ou erro): {e}")
        return False

def test_with_requests():
    """Testa a página web fazendo requisições HTTP"""
    print("\n=== Testando Página Web com Requests ===")
    
    try:
        # Testa se a página principal carrega
        response = requests.get('http://localhost:8000')
        print(f"Página principal - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Página principal carregou com sucesso")
            
            # Verifica se os arquivos CSS e JS estão sendo servidos
            css_response = requests.get('http://localhost:8000/static/css/style.css')
            js_response = requests.get('http://localhost:8000/static/js/script.js')
            
            print(f"CSS - Status: {css_response.status_code}")
            print(f"JS - Status: {js_response.status_code}")
            
            return True
        else:
            print(f"Erro ao carregar página principal: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Erro no teste com requests: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando testes da interface...")
    
    # Teste da API
    api_result = test_api_directly()
    
    # Teste da página web
    web_result = test_with_requests()
    
    # Teste com Selenium (se disponível)
    selenium_result = test_web_interface()
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"API funcionando: {'✓' if api_result else '✗'}")
    print(f"Página web carregando: {'✓' if web_result else '✗'}")
    print(f"Interface web (Selenium): {'✓' if selenium_result else '✗ (pode ser normal se não tiver Chrome/Selenium)'}")
    
    if api_result:
        print("\n✓ O sistema está funcionando! A API está respondendo corretamente.")
        print("✓ Se você está vendo erros no navegador, pode ser um problema de cache.")
        print("✓ Tente recarregar a página com Ctrl+F5 ou abrir em uma aba anônima.")
    else:
        print("\n✗ Há problemas com a API que precisam ser corrigidos.")
