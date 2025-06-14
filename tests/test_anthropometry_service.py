import unittest
from datetime import date
from app.services.anthropometry_service import AnthropometryService
from app.models import IndividuoBase

class TestAnthropometryService(unittest.TestCase):

    def setUp(self):
        # Para testes unitários do serviço, podemos instanciá-lo sem uma sessão de DB
        # se as funções testadas não dependerem diretamente do DB (ou mockar o DB).
        self.service = AnthropometryService(db=None)

    def test_calculate_age_exact(self):
        # Exemplos da p.18 da Norma Técnica do SISVAN (2011)
        # "Uma criança com 2 anos, 11 meses e 29 dias terá 2 anos e 11 meses completos."
        # "Uma criança com 11 meses e 29 dias terá 11 meses completos."
        # "Uma criança com 29 dias de vida terá 0 meses completos."

        # Caso 1: 2 anos, 11 meses, 29 dias
        dob1 = date(2020, 1, 1)
        eval_date1 = date(2022, 12, 30) # 2 anos, 11 meses, 29 dias
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob1, eval_date1)
        self.assertEqual(anos, 2)
        self.assertEqual(meses, 11)
        self.assertEqual(dias, 29)
        self.assertEqual(total_meses, 35) # 2*12 + 11
        self.assertEqual(total_dias, (eval_date1 - dob1).days)
        self.assertIn("2 anos", age_str)
        self.assertIn("11 meses", age_str)
        # self.assertNotIn("29 dias", age_str) # A string deve focar em anos e meses completos

        # Caso 2: 11 meses, 29 dias
        dob2 = date(2021, 1, 1)
        # Caso 2: 11 meses, 29 dias
        dob2 = date(2021, 1, 1)
        eval_date2 = date(2021, 12, 30) # 0 anos, 11 meses, 29 dias
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob2, eval_date2)
        self.assertEqual(dias, 29)
        self.assertEqual(total_meses, 11)
        self.assertIn("11 meses", age_str)
        # self.assertNotIn("29 dias", age_str) # A string deve focar em meses completos

        # Caso 3: 29 dias de vida
        dob3 = date(2022, 12, 1)
        eval_date3 = date(2022, 12, 30) # 0 anos, 0 meses, 29 dias
        # Caso 3: 29 dias de vida
        dob3 = date(2022, 12, 1)
        eval_date3 = date(2022, 12, 30) # 0 anos, 0 meses, 29 dias
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob3, eval_date3)
        self.assertEqual(age_str, "29 dias") # Para <1 mês, mostrar dias

        # Caso 4: Exatamente 1 mês
        # Caso 4: Exatamente 1 mês
        dob4 = date(2022, 11, 15)
        eval_date4 = date(2022, 12, 15)
        anos, meses, dias, age_str, total_meses, total_dias = self.service.calculate_age_exact(dob4, eval_date4)
        result1 = self.service.calculate_imc(15.5, 95.3)
        self.assertIsNotNone(result1)
        if result1 is not None:
            self.assertAlmostEqual(result1, 17.06, places=2)
        result2 = self.service.calculate_imc(60, 165)
        self.assertIsNotNone(result2)
        if result2 is not None:
            self.assertAlmostEqual(result2, 22.04, places=2)
        self.assertIsNone(self.service.calculate_imc(10, 0)) # Altura zero

    def test_process_individual_data_structure(self):
        # Teste básico para verificar se a estrutura do resultado é retornada
        # sem depender do banco de dados (usando os placeholders do serviço)
        data = IndividuoBase(
            nome="Teste Criança",
            data_nascimento=date(2020, 6, 15),
            data_avaliacao=date(2023, 1, 10),
            sexo="M",
            peso_kg=15.0,
            altura_cm=90.0
        )
        resultado = self.service.process_individual_data(data)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.dados_entrada.nome, "Teste Criança")
        self.assertIn("anos", resultado.idade_calculada_str)
        self.assertTrue(len(resultado.indicadores) > 0) # Espera-se P/I, A/I, IMC/I
        
        # Verificar se o IMC foi calculado
        self.assertIsNotNone(resultado.imc_calculado)

        # Verificar se os indicadores têm os campos esperados
        for indicador in resultado.indicadores:
            self.assertIn(indicador.tipo, ["Peso-para-Idade (P/I)", "Altura-para-Idade (A/I)", "IMC-para-Idade (IMC/I)"])
            self.assertIsNotNone(indicador.classificacao) # Mesmo que seja placeholder

    # TODO: Adicionar mais testes, especialmente quando a lógica de DB for implementada.
    # Para isso, você precisará mockar a sessão do DB e as queries.
    # from unittest.mock import MagicMock
    #
    # def test_get_z_score_with_db_mock(self):
    #     mock_db_session = MagicMock()
    #     # Configurar o mock para retornar dados de referência simulados
    #     # mock_db_session.query(...).filter(...).first.return_value = ...
    #     service_with_mock_db = AnthropometryService(db=mock_db_session)
    #     # Chamar a função que usa o DB
    #     z_score, classification = service_with_mock_db.get_z_score_and_classification(...)
    #     self.assertIsNotNone(z_score)

if __name__ == '__main__':
    unittest.main()