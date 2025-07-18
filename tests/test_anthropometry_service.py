import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from app.services.anthropometry_service import AnthropometryService
from app.models import IndividuoBase, ResultadoProcessamentoIndividual, Indicador, SexoEnum

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
            self.assertAlmostEqual(result1, 17.07, places=2)
        result2 = self.service.calculate_imc(60, 165)
        self.assertIsNotNone(result2)
        if result2 is not None:
            self.assertAlmostEqual(result2, 22.04, places=2)
        self.assertIsNone(self.service.calculate_imc(10, 0)) # Altura zero    def test_process_individual_data_structure(self):
        # Teste básico para verificar se a estrutura do resultado é retornada
        # sem depender do banco de dados (usando os placeholders do serviço)
        data = IndividuoBase(
            nome="Teste Criança",
            data_nascimento=date(2020, 6, 15),
            data_avaliacao=date(2023, 1, 10),
            sexo=SexoEnum.M,
            peso_kg=Decimal("15.0"),
            altura_cm=Decimal("90.0")
        )        # Converter para IndividuoCreate para o serviço
        from app.models import IndividuoCreate
        data_create = IndividuoCreate(
            nome="Teste Criança",  # usar string diretamente
            data_nascimento=data.data_nascimento,
            data_avaliacao=data.data_avaliacao,
            sexo=data.sexo,
            peso_kg=data.peso_kg,
            altura_cm=data.altura_cm
        )
        resultado = self.service.process_individual_data(data_create)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nome, "Teste Criança")
        self.assertIn("anos", resultado.idade)
        self.assertTrue(len(resultado.indicadores) > 0) # Espera-se P/I, A/I, IMC/I
        
        # Verificar se o IMC foi calculado
        self.assertIsNotNone(resultado.imc)

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

# New Test Class for process_batch_data
class TestAnthropometryServiceBatchProcessing(unittest.TestCase):

    # This helper might not be strictly necessary if the mock for process_individual_data
    # is simple and directly returns a generic success object.
    # However, if we want the mock to return data that reflects the input row, it could be useful.
    # For now, the mock_process_individual_data.side_effect in the first test is more direct.
    # def _get_mock_successful_individual_result(self, row_data_dict):
    #     return ResultadoProcessamentoIndividual(
    #         dados_entrada=IndividuoBase(
    #             nome=row_data_dict.get("nome"), # Use .get for optional fields
    #             data_nascimento=date.fromisoformat(row_data_dict["data_nascimento"]),
    #             data_avaliacao=date.fromisoformat(row_data_dict["data_avaliacao"]),
    #             sexo=row_data_dict["sexo"].upper(),
    #             peso_kg=float(str(row_data_dict["peso_kg"]).replace(",",".")),
    #             altura_cm=float(str(row_data_dict["altura_cm"]).replace(",","."))
    #         ),
    #         idade_calculada_str="1 ano", idade_anos=1, idade_meses=0, idade_dias=0,
    #         imc_calculado=15.62,
    #         indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=10, escore_z=0.5, classificacao="Eutrófico")]
    #     )

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_valid_data(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "nome,data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "Alice,2022-01-01,2023-01-01,F,10,80\n"
            "Bob,2021-05-10,2023-05-10,M,12.5,85.5"
        )

        # Configure mock based on actual input it would receive
        def side_effect_func(individuo_base_instance):
            # Simulate processing based on the Pydantic model passed to it
            return ResultadoProcessamentoIndividual(
                dados_entrada=individuo_base_instance, # The Pydantic model instance itself
                idade_calculada_str="1 ano", # Dummy value
                idade_anos=1, idade_meses=0, idade_dias=0, # Dummy values
                imc_calculado=15.62, # Dummy value
                indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=individuo_base_instance.peso_kg, escore_z=0.5, classificacao="Eutrófico")]
            )
        mock_process_individual_data.side_effect = side_effect_func

        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "valid_data.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 2)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Alice")
        # IndividuoBase validator for 'sexo' ensures it's uppercased.
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.nome, "Bob")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "M")


# New Test Class for process_batch_data
class TestAnthropometryServiceBatchProcessing(unittest.TestCase):

    # This helper might not be strictly necessary if the mock for process_individual_data
    # is simple and directly returns a generic success object.
    # However, if we want the mock to return data that reflects the input row, it could be useful.
    # For now, the mock_process_individual_data.side_effect in the first test is more direct.
    # def _get_mock_successful_individual_result(self, row_data_dict):
    #     return ResultadoProcessamentoIndividual(
    #         dados_entrada=IndividuoBase(
    #             nome=row_data_dict.get("nome"), # Use .get for optional fields
    #             data_nascimento=date.fromisoformat(row_data_dict["data_nascimento"]),
    #             data_avaliacao=date.fromisoformat(row_data_dict["data_avaliacao"]),
    #             sexo=row_data_dict["sexo"].upper(),
    #             peso_kg=float(str(row_data_dict["peso_kg"]).replace(",",".")),
    #             altura_cm=float(str(row_data_dict["altura_cm"]).replace(",","."))
    #         ),
    #         idade_calculada_str="1 ano", idade_anos=1, idade_meses=0, idade_dias=0,
    #         imc_calculado=15.62,
    #         indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=10, escore_z=0.5, classificacao="Eutrófico")]
    #     )

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_valid_data(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "nome,data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "Alice,2022-01-01,2023-01-01,F,10,80\n"
            "Bob,2021-05-10,2023-05-10,M,12.5,85.5"
        )

        def side_effect_func(individuo_base_instance):
            return ResultadoProcessamentoIndividual(
                dados_entrada=individuo_base_instance,
                idade_calculada_str="1 ano",
                idade_anos=1, idade_meses=0, idade_dias=0,
                imc_calculado=15.62,
                indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=individuo_base_instance.peso_kg, escore_z=0.5, classificacao="Eutrófico")]
            )
        mock_process_individual_data.side_effect = side_effect_func

        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "valid_data.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 2)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Alice")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.nome, "Bob")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "M")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_dates(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-15,2023-01-15,F,10,80\n"       # YYYY-MM-DD
            "16/02/2022,16/02/2023,M,11,82\n"       # DD/MM/YYYY
            "03/17/2022,03/17/2023,F,12,84\n"       # MM/DD/YYYY
            "18-04-2022,18-04-2023,M,13,86"        # DD-MM-YYYY
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_dates.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        # Check one date to ensure parsing worked as expected by mock
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.data_nascimento, date(2022,2,16))

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_numerics(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,F,10.5,80.1\n"
            "2022-01-02,2023-01-02,M,\"1.234,56\",\"120,5\"\n"
            "2022-01-03,2023-01-03,F,\"1,234.56\",\"110.7\"\n"
            "2022-01-04,2023-01-04,M,12,88\n"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_numerics.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertAlmostEqual(result["resultados_individuais"][0].dados_entrada.peso_kg, 10.5)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.altura_cm, 120.5)
        self.assertAlmostEqual(result["resultados_individuais"][2].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][3].dados_entrada.peso_kg, 12)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_sex_values(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,Masculino,10,80\n"
            "2022-01-02,2023-01-02,female,11,82\n"
            "2022-01-03,2023-01-03,m,12,84\n"
            "2022-01-04,2023-01-04,F,13,86"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_sex.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][2].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][3].dados_entrada.sexo, "F")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_headers(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "NOME COMPLETO,data de nascimento,DATA DA AVALIACAO,Gender,PESO (KG),Altura (cm)\n"
            "Flex Header Test,2022-01-01,2023-01-01,M,10,80"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_headers.csv")

        self.assertEqual(result["total_rows_attempted"], 1)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Flex Header Test")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")


# New Test Class for process_batch_data
class TestAnthropometryServiceBatchProcessing(unittest.TestCase):

    # This helper might not be strictly necessary if the mock for process_individual_data
    # is simple and directly returns a generic success object.
    # However, if we want the mock to return data that reflects the input row, it could be useful.
    # For now, the mock_process_individual_data.side_effect in the first test is more direct.
    # def _get_mock_successful_individual_result(self, row_data_dict):
    #     return ResultadoProcessamentoIndividual(
    #         dados_entrada=IndividuoBase(
    #             nome=row_data_dict.get("nome"), # Use .get for optional fields
    #             data_nascimento=date.fromisoformat(row_data_dict["data_nascimento"]),
    #             data_avaliacao=date.fromisoformat(row_data_dict["data_avaliacao"]),
    #             sexo=row_data_dict["sexo"].upper(),
    #             peso_kg=float(str(row_data_dict["peso_kg"]).replace(",",".")),
    #             altura_cm=float(str(row_data_dict["altura_cm"]).replace(",","."))
    #         ),
    #         idade_calculada_str="1 ano", idade_anos=1, idade_meses=0, idade_dias=0,
    #         imc_calculado=15.62,
    #         indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=10, escore_z=0.5, classificacao="Eutrófico")]
    #     )

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_valid_data(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "nome,data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "Alice,2022-01-01,2023-01-01,F,10,80\n"
            "Bob,2021-05-10,2023-05-10,M,12.5,85.5"
        )

        def side_effect_func(individuo_base_instance):
            return ResultadoProcessamentoIndividual(
                dados_entrada=individuo_base_instance,
                idade_calculada_str="1 ano",
                idade_anos=1, idade_meses=0, idade_dias=0,
                imc_calculado=15.62,
                indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=individuo_base_instance.peso_kg, escore_z=0.5, classificacao="Eutrófico")]
            )
        mock_process_individual_data.side_effect = side_effect_func

        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "valid_data.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 2)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Alice")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.nome, "Bob")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "M")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_dates(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-15,2023-01-15,F,10,80\n"       # YYYY-MM-DD
            "16/02/2022,16/02/2023,M,11,82\n"       # DD/MM/YYYY
            "03/17/2022,03/17/2023,F,12,84\n"       # MM/DD/YYYY
            "18-04-2022,18-04-2023,M,13,86"        # DD-MM-YYYY
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_dates.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.data_nascimento, date(2022,2,16))

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_numerics(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,F,10.5,80.1\n"
            "2022-01-02,2023-01-02,M,\"1.234,56\",\"120,5\"\n"
            "2022-01-03,2023-01-03,F,\"1,234.56\",\"110.7\"\n"
            "2022-01-04,2023-01-04,M,12,88\n"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_numerics.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertAlmostEqual(result["resultados_individuais"][0].dados_entrada.peso_kg, 10.5)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.altura_cm, 120.5)
        self.assertAlmostEqual(result["resultados_individuais"][2].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][3].dados_entrada.peso_kg, 12)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_sex_values(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,Masculino,10,80\n"
            "2022-01-02,2023-01-02,female,11,82\n"
            "2022-01-03,2023-01-03,m,12,84\n"
            "2022-01-04,2023-01-04,F,13,86"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_sex.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][2].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][3].dados_entrada.sexo, "F")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_headers(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "NOME COMPLETO,data de nascimento,DATA DA AVALIACAO,Gender,PESO (KG),Altura (cm)\n"
            "Flex Header Test,2022-01-01,2023-01-01,M,10,80"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_headers.csv")

        self.assertEqual(result["total_rows_attempted"], 1)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Flex Header Test")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_date(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "INVALID-DATE,2023-01-02,F,11,82"
        )
        # Mock only for the valid row
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8') # Corrected encoding
        result = service.process_batch_data(file_content_bytes, "invalid_date_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1) # Only first row is valid
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("não pôde ser analisada com os formatos conhecidos", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["data_nascimento"], "INVALID-DATE")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_number(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,F,INVALID-NUMBER,82"
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "invalid_number_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Não foi possível converter a string numérica para float", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["peso_kg"], "INVALID-NUMBER")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_sex(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,INVALIDSEX,12,82"
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "invalid_sex_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Sexo deve ser \"M\" ou \"F\"", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["sexo"], "INVALIDSEX")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_missing_required_value(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,F,,82" # Missing peso_kg
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "missing_value.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Campo obrigatório 'peso_kg'", error_info["erro"])
        self.assertIn("está vazio na linha 3", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["peso_kg"], "")


# New Test Class for process_batch_data
class TestAnthropometryServiceBatchProcessing(unittest.TestCase):

    # This helper might not be strictly necessary if the mock for process_individual_data
    # is simple and directly returns a generic success object.
    # However, if we want the mock to return data that reflects the input row, it could be useful.
    # For now, the mock_process_individual_data.side_effect in the first test is more direct.
    # def _get_mock_successful_individual_result(self, row_data_dict):
    #     return ResultadoProcessamentoIndividual(
    #         dados_entrada=IndividuoBase(
    #             nome=row_data_dict.get("nome"), # Use .get for optional fields
    #             data_nascimento=date.fromisoformat(row_data_dict["data_nascimento"]),
    #             data_avaliacao=date.fromisoformat(row_data_dict["data_avaliacao"]),
    #             sexo=row_data_dict["sexo"].upper(),
    #             peso_kg=float(str(row_data_dict["peso_kg"]).replace(",",".")),
    #             altura_cm=float(str(row_data_dict["altura_cm"]).replace(",","."))
    #         ),
    #         idade_calculada_str="1 ano", idade_anos=1, idade_meses=0, idade_dias=0,
    #         imc_calculado=15.62,
    #         indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=10, escore_z=0.5, classificacao="Eutrófico")]
    #     )

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_valid_data(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "nome,data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "Alice,2022-01-01,2023-01-01,F,10,80\n"
            "Bob,2021-05-10,2023-05-10,M,12.5,85.5"
        )

        def side_effect_func(individuo_base_instance):
            return ResultadoProcessamentoIndividual(
                dados_entrada=individuo_base_instance,
                idade_calculada_str="1 ano",
                idade_anos=1, idade_meses=0, idade_dias=0,
                imc_calculado=15.62,
                indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=individuo_base_instance.peso_kg, escore_z=0.5, classificacao="Eutrófico")]
            )
        mock_process_individual_data.side_effect = side_effect_func

        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "valid_data.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 2)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Alice")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.nome, "Bob")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "M")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_dates(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-15,2023-01-15,F,10,80\n"       # YYYY-MM-DD
            "16/02/2022,16/02/2023,M,11,82\n"       # DD/MM/YYYY
            "03/17/2022,03/17/2023,F,12,84\n"       # MM/DD/YYYY
            "18-04-2022,18-04-2023,M,13,86"        # DD-MM-YYYY
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_dates.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.data_nascimento, date(2022,2,16))

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_numerics(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,F,10.5,80.1\n"
            "2022-01-02,2023-01-02,M,\"1.234,56\",\"120,5\"\n"
            "2022-01-03,2023-01-03,F,\"1,234.56\",\"110.7\"\n"
            "2022-01-04,2023-01-04,M,12,88\n"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_numerics.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertAlmostEqual(result["resultados_individuais"][0].dados_entrada.peso_kg, 10.5)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][1].dados_entrada.altura_cm, 120.5)
        self.assertAlmostEqual(result["resultados_individuais"][2].dados_entrada.peso_kg, 1234.56)
        self.assertAlmostEqual(result["resultados_individuais"][3].dados_entrada.peso_kg, 12)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_sex_values(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,Masculino,10,80\n"
            "2022-01-02,2023-01-02,female,11,82\n"
            "2022-01-03,2023-01-03,m,12,84\n"
            "2022-01-04,2023-01-04,F,13,86"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_sex.csv")

        self.assertEqual(result["total_rows_attempted"], 4)
        self.assertEqual(len(result["resultados_individuais"]), 4)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][1].dados_entrada.sexo, "F")
        self.assertEqual(result["resultados_individuais"][2].dados_entrada.sexo, "M")
        self.assertEqual(result["resultados_individuais"][3].dados_entrada.sexo, "F")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_flexible_headers(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "NOME COMPLETO,data de nascimento,DATA DA AVALIACAO,Gender,PESO (KG),Altura (cm)\n"
            "Flex Header Test,2022-01-01,2023-01-01,M,10,80"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "flex_headers.csv")

        self.assertEqual(result["total_rows_attempted"], 1)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 0)
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.nome, "Flex Header Test")
        self.assertEqual(result["resultados_individuais"][0].dados_entrada.sexo, "M")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_date(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "INVALID-DATE,2023-01-02,F,11,82"
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "invalid_date_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("não pôde ser analisada com os formatos conhecidos", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["data_nascimento"], "INVALID-DATE")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_number(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,F,INVALID-NUMBER,82"
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "invalid_number_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Não foi possível converter a string numérica para float", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["peso_kg"], "INVALID-NUMBER")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_invalid_sex(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,INVALIDSEX,12,82"
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "invalid_sex_row.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Sexo deve ser \"M\" ou \"F\"", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["sexo"], "INVALIDSEX")

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_row_with_missing_required_value(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"
            "2022-01-02,2023-01-02,F,,82" # Missing peso_kg
        )
        mock_process_individual_data.return_value = ResultadoProcessamentoIndividual(
            dados_entrada=IndividuoBase(data_nascimento=date(2022,1,1),data_avaliacao=date(2023,1,1),sexo="M",peso_kg=10,altura_cm=80),
            idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "missing_value.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)
        error_info = result["erros_por_linha"][0]
        self.assertEqual(error_info["linha"], 3)
        self.assertIn("Campo obrigatório 'peso_kg'", error_info["erro"])
        self.assertIn("está vazio na linha 3", error_info["erro"])
        self.assertEqual(error_info["dados_originais"]["peso_kg"], "")

    def test_process_batch_missing_required_header_in_file(self):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,peso_kg,altura_cm\n" # Missing 'sexo'
            "2022-01-01,2023-01-01,10,80"
        )
        file_content_bytes = csv_content.encode('utf-8')
        with self.assertRaises(ValueError) as context:
            service.process_batch_data(file_content_bytes, "missing_header.csv")
        self.assertIn("Cabeçalhos obrigatórios ausentes", str(context.exception))
        self.assertIn("'sexo'", str(context.exception))

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_empty_file(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = ""
        file_content_bytes = csv_content.encode('utf-8')

        with self.assertRaises(ValueError) as context:
             service.process_batch_data(file_content_bytes, "empty.csv")
        self.assertIn("está vazio ou não contém cabeçalho", str(context.exception))

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_file_with_only_headers(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm"
        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "only_headers.csv")

        self.assertEqual(result["total_rows_attempted"], 0)
        self.assertEqual(len(result["resultados_individuais"]), 0)
        self.assertEqual(len(result["erros_por_linha"]), 0)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_file_utf8_bom(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,F,10,80"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = b'\xef\xbb\xbf' + csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "bom_test.csv")

        self.assertEqual(result["total_rows_attempted"], 1)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 0)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_tsv_file(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        tsv_content = (
            "data_nascimento\tdata_avaliacao\tsexo\tpeso_kg\taltura_cm\n"
            "2022-03-03\t2023-03-03\tM\t14.5\t92.0"
        )
        mock_process_individual_data.side_effect = lambda ib: ResultadoProcessamentoIndividual(
            dados_entrada=ib, idade_calculada_str="1y", idade_anos=1,idade_meses=0,idade_dias=0,imc_calculado=15,indicadores=[]
        )
        file_content_bytes = tsv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "test.tsv")

        self.assertEqual(result["total_rows_attempted"], 1)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 0)

    @patch.object(AnthropometryService, 'process_individual_data')
    def test_process_batch_internal_error_in_individual_processing(self, mock_process_individual_data):
        service = AnthropometryService(db=None)
        csv_content = (
            "data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm\n"
            "2022-01-01,2023-01-01,M,10,80\n"      # Success
            "2022-02-02,2023-02-02,F,12,85"       # This row will cause simulated error
        )

        def side_effect_for_error(individuo_base_instance):
            if individuo_base_instance.sexo == "F":
                raise ValueError("Simulated error in individual processing")
            # Correctly create an IndividuoBase for the successful case to be passed to ResultadoProcessamentoIndividual
            return ResultadoProcessamentoIndividual(
                dados_entrada=individuo_base_instance, # Pass the actual instance
                idade_calculada_str="1 ano", idade_anos=1, idade_meses=0, idade_dias=0, imc_calculado=15.62,
                indicadores=[IndicadorCalculado(tipo="P/I", valor_medido=individuo_base_instance.peso_kg, escore_z=0.5, classificacao="Eutrófico")]
            )
        mock_process_individual_data.side_effect = side_effect_for_error

        file_content_bytes = csv_content.encode('utf-8')
        result = service.process_batch_data(file_content_bytes, "internal_error_test.csv")

        self.assertEqual(result["total_rows_attempted"], 2)
        self.assertEqual(len(result["resultados_individuais"]), 1)
        self.assertEqual(len(result["erros_por_linha"]), 1)

        error_detail = result["erros_por_linha"][0]
        self.assertEqual(error_detail["linha"], 3)
        self.assertIn("Simulated error in individual processing", error_detail["erro"])
        self.assertEqual(error_detail["dados_originais"]["sexo"], "F")


if __name__ == '__main__':
    unittest.main()