#!/usr/bin/env python3

"""
Teste simples da funcionalidade com banco de dados.
"""

from decimal import Decimal
from datetime import date
from app.db.session import SessionLocal
from app.services.anthropometry_service import AnthropometryService
from app.models import IndividuoCreate, SexoEnum

def main():
    print("=== Teste de Funcionalidade com Banco de Dados ===")
    
    # Criar sessão do banco
    db = SessionLocal()
    try:
        # Criar serviço
        service = AnthropometryService(db=db)
        
        # Dados de teste
        test_data = IndividuoCreate(
            nome="João Teste",
            data_nascimento=date(2020, 1, 1),
            data_avaliacao=date(2023, 1, 1),
            sexo=SexoEnum.M,
            peso_kg=Decimal("15.0"),
            altura_cm=Decimal("90.0")
        )
        
        print(f"Processando dados para: {test_data.nome}")
        print(f"Nascimento: {test_data.data_nascimento}")
        print(f"Avaliação: {test_data.data_avaliacao}")
        print(f"Peso: {test_data.peso_kg} kg")
        print(f"Altura: {test_data.altura_cm} cm")
        
        # Processar dados
        resultado = service.process_individual_data(test_data)
        
        print("\n=== RESULTADO ===")
        print(f"Nome: {resultado.nome}")
        print(f"Sexo: {resultado.sexo}")
        print(f"Idade: {resultado.idade}")
        print(f"IMC: {resultado.imc}")
        print(f"Quantidade de indicadores: {len(resultado.indicadores)}")
        
        print("\n=== INDICADORES ===")
        for indicador in resultado.indicadores:
            print(f"- {indicador.tipo}: {indicador.valor_observado} (Z-score: {indicador.escore_z}) - {indicador.classificacao}")
            
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
