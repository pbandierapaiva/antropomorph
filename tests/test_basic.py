import unittest
from datetime import date
from decimal import Decimal
from app.services.anthropometry_service import AnthropometryService
from app.models import IndividuoCreate, SexoEnum

class TestAnthropometryService(unittest.TestCase):

    def setUp(self):
        self.service = AnthropometryService(db=None)

    def test_calculate_age_exact(self):
        """Testa cálculo de idade exata"""
        # Caso 1: 2 anos, 11 meses, 29 dias
        dob1 = date(2020, 1, 1)
        eval_date1 = date(2022, 12, 30)
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob1, eval_date1)
        self.assertEqual(anos, 2)
        self.assertEqual(meses, 11)
        self.assertEqual(dias, 29)
        self.assertEqual(total_meses, 35)  # 2*12 + 11
        self.assertEqual(total_dias, (eval_date1 - dob1).days)
        self.assertIn("2 anos", age_str)
        self.assertIn("11 meses", age_str)

        # Caso 2: 11 meses, 29 dias
        dob2 = date(2021, 1, 1)
        eval_date2 = date(2021, 12, 30)
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob2, eval_date2)
        self.assertEqual(dias, 29)
        self.assertEqual(total_meses, 11)
        self.assertIn("11 meses", age_str)

        # Caso 3: 29 dias de vida
        dob3 = date(2022, 12, 1)
        eval_date3 = date(2022, 12, 30)
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob3, eval_date3)
        self.assertEqual(age_str, "29 dias")

    def test_calculate_imc(self):
        """Testa cálculo de IMC"""
        result1 = self.service.calculate_imc(15.5, 95.3)
        self.assertIsNotNone(result1)
        if result1 is not None:
            self.assertAlmostEqual(result1, 17.07, places=2)
        
        result2 = self.service.calculate_imc(60, 165)
        self.assertIsNotNone(result2)
        if result2 is not None:
            self.assertAlmostEqual(result2, 22.04, places=2)
        
        # Altura zero deve retornar None
        self.assertIsNone(self.service.calculate_imc(10, 0))

    def test_process_individual_data_structure(self):
        """Testa estrutura do resultado do processamento individual"""
        data = IndividuoCreate(
            nome="Teste Criança",
            data_nascimento=date(2020, 6, 15),
            data_avaliacao=date(2023, 1, 10),
            sexo=SexoEnum.M,
            peso_kg=Decimal("15.0"),
            altura_cm=Decimal("90.0")
        )
        
        resultado = self.service.process_individual_data(data)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Teste Criança")
        self.assertIn("anos", resultado.idade)
        self.assertTrue(len(resultado.indicadores) > 0)
        self.assertIsNotNone(resultado.imc)

        # Para testes sem DB, os indicadores serão placeholders
        for indicador in resultado.indicadores:
            self.assertIn("Teste-", indicador.tipo)
            self.assertEqual(indicador.classificacao, "Teste - Sem DB")

if __name__ == '__main__':
    unittest.main()
