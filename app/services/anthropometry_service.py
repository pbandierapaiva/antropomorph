import os
import sys
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Tuple, Dict, Optional, List
from sqlalchemy.orm import Session

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.models import (
    IndividuoBase, 
    ResultadoProcessamentoIndividual, 
    IndicadorCalculado,
    TabelaReferenciaSISVAN, # Modelo SQLAlchemy para valores Z
    TabelaClassificacao,   # Modelo SQLAlchemy para regras de classificação
    SexoEnumDB             # Enum para sexo no DB
)

# (Se você precisar de pandas para CSV, mas o serviço principal não usa diretamente)
# import pandas as pd
# import io

class AnthropometryService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db  # Sessão do banco de dados injetada

    def calculate_age_exact(self, dob: date, assessment_date: date) -> Tuple[int, int, int, str, int, int]:
        """
        Calcula a idade precisa em anos, meses e dias.
        Retorna (anos, meses, dias, string_formatada, total_meses_completos, total_dias_vida).
        """
        if assessment_date < dob:
            raise ValueError("Data de avaliação não pode ser anterior à data de nascimento.")

        delta = relativedelta(assessment_date, dob)
        anos = delta.years
        meses_componente = delta.months # 'meses' do componente da idade, não total
        dias_componente = delta.days   # 'dias' do componente da idade

        total_meses_completos = anos * 12 + meses_componente
        total_dias_vida = (assessment_date - dob).days

        age_str_parts = []
        if anos > 0:
            age_str_parts.append(f"{anos} ano{'s' if anos > 1 else ''}")
        if meses_componente > 0:
            age_str_parts.append(f"{meses_componente} {'mes' if meses_componente == 1 else 'meses'}")
        
        # Adicionar dias apenas se for relevante (ex: < 1 mês ou para completar a string)
        # Ou se a política for sempre mostrar os dias
        if dias_componente > 0:
             if not age_str_parts: # Se não há anos nem meses, mostra só dias
                 age_str_parts.append(f"{dias_componente} dia{'s' if dias_componente > 1 else ''}")
             # else: # Opcional: adicionar dias mesmo se houver anos/meses
             #    age_str_parts.append(f"{dias_componente} dia{'s' if dias_componente > 1 else ''}")


        age_str = ", ".join(age_str_parts)
        if not age_str: # Caso de recém-nascido no mesmo dia do nascimento
            age_str = "0 dias"
        
        return anos, meses_componente, dias_componente, age_str, total_meses_completos, total_dias_vida

    def calculate_imc(self, peso_kg: float, altura_cm: float) -> Optional[float]:
        if altura_cm <= 0:
            return None
        altura_m = altura_cm / 100
        imc = peso_kg / (altura_m ** 2)
        return round(imc, 2)

    def get_z_score_range_and_classification(
        self,
        indicador_map_key: str, 
        sexo_db: SexoEnumDB,
        idade_total_meses: int,
        medida_valor: float
    ) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        """
        Determina a faixa de Z-score em que a medida_valor se encontra,
        um Z-score representativo para classificação, e a classificação.
        Não faz interpolação fracionada, usa os Z-scores discretos da tabela.
        Retorna (z_score_para_classificacao, classificacao_str, faixa_z_descritiva)
        """
        print(f"\n[SERVICE DEBUG] Buscando Z-score para: ind='{indicador_map_key}', sexo='{sexo_db.value}', idade_meses={idade_total_meses}, medida={medida_valor}")

        if self.db is None:
            print("[SERVICE DEBUG] ERRO CRÍTICO: self.db é None! A conexão com o banco de dados não foi estabelecida no serviço.")
            # Este retorno é um fallback, mas não deveria acontecer em produção.
            return 0.0, "Erro: DB não conectado", "Faixa Z não determinada (DB)"

        ref_values_db = self.db.query(TabelaReferenciaSISVAN).filter(
            TabelaReferenciaSISVAN.indicador == indicador_map_key,
            TabelaReferenciaSISVAN.sexo == sexo_db,
            TabelaReferenciaSISVAN.idade_meses == idade_total_meses
        ).first()

        if not ref_values_db:
            print(f"[SERVICE DEBUG] Dados de referência (valores Z) NÃO encontrados no DB para os parâmetros acima.")
            return None, "Dados de referência não encontrados", None # Modificado para retornar 3 valores
        else:
            print(f"[SERVICE DEBUG] Dados de referência encontrados: Idade={ref_values_db.idade_meses}, Z0={ref_values_db.valor_z_0}, Z-3={ref_values_db.valor_z_neg_3}, Z+3={ref_values_db.valor_z_pos_3}")

        z_map_ordered = [
            {'measure': ref_values_db.valor_z_neg_3, 'z': -3.0, 'label': "Z=-3"},
            {'measure': ref_values_db.valor_z_neg_2, 'z': -2.0, 'label': "Z=-2"},
            {'measure': ref_values_db.valor_z_neg_1, 'z': -1.0, 'label': "Z=-1"},
            {'measure': ref_values_db.valor_z_0,     'z':  0.0, 'label': "Z=0 (Mediana)"},
            {'measure': ref_values_db.valor_z_pos_1, 'z':  1.0, 'label': "Z=+1"},
            {'measure': ref_values_db.valor_z_pos_2, 'z':  2.0, 'label': "Z=+2"},
            {'measure': ref_values_db.valor_z_pos_3, 'z':  3.0, 'label': "Z=+3"}
        ]

        valid_points = [p for p in z_map_ordered if p['measure'] is not None]
        
        # Garantir que os pontos válidos estejam ordenados pela medida (devem estar, mas por segurança)
        # Isso é crucial se houver 'None's no meio, pois a ordem original dos Zs deve ser mantida
        # E depois filtramos os 'None's. A ordenação dos Zs já é inerente.
        # A ordenação por 'measure' seria se fôssemos interpolar, mas aqui comparamos com faixas.

        if not valid_points:
            print(f"[SERVICE DEBUG] Nenhum ponto de referência (valor Z) válido encontrado no DB para os parâmetros.")
            return None, "Valores de referência Z ausentes", None

        z_score_para_classificacao = None
        faixa_z_desc = "Faixa Z não determinada"

        # Caso 1: Medida abaixo do menor ponto de referência válido (ex: abaixo do valor para Z=-3)
        if medida_valor < valid_points[0]['measure']:
            z_score_para_classificacao = valid_points[0]['z'] # Usa o Z do limite mais baixo
            faixa_z_desc = f"< {valid_points[0]['label']} (Medida {medida_valor:.2f} < {valid_points[0]['measure']:.2f})"
        # Caso 2: Medida acima ou igual ao maior ponto de referência válido (ex: acima ou igual ao valor para Z=+3)
        elif medida_valor >= valid_points[-1]['measure']:
            z_score_para_classificacao = valid_points[-1]['z'] # Usa o Z do limite mais alto
            faixa_z_desc = f">= {valid_points[-1]['label']} (Medida {medida_valor:.2f} >= {valid_points[-1]['measure']:.2f})"
        # Caso 3: Medida está entre dois pontos de referência
        else:
            for i in range(len(valid_points) - 1):
                lower_bound = valid_points[i]
                upper_bound = valid_points[i+1]
                # Se a medida é maior ou igual à medida do Z inferior E menor que a medida do Z superior
                if lower_bound['measure'] <= medida_valor < upper_bound['measure']:
                    # A medida está na faixa [Z_lower, Z_upper).
                    # Para classificação SISVAN, o Z-score do limite inferior da faixa é geralmente usado.
                    z_score_para_classificacao = lower_bound['z']
                    faixa_z_desc = f"Entre {lower_bound['label']} ({lower_bound['measure']:.2f}) e {upper_bound['label']} (<{upper_bound['measure']:.2f})"
                    break
        
        if z_score_para_classificacao is None:
             print(f"[SERVICE DEBUG] Não foi possível determinar a faixa de Z-score para medida {medida_valor:.2f} com os pontos: {valid_points}")
             return None, "Faixa de Z-score não determinada", None

        print(f"[SERVICE DEBUG] Z-score pontual para classificação: {z_score_para_classificacao}, Faixa: {faixa_z_desc}")

        classificacao_str = "Classificação não encontrada"
        if z_score_para_classificacao is not None:
            # A TabelaClassificacao espera um Z-score PONTUAL e define intervalos [min, max)
            # Ex: Magreza: z_min = -3, z_max = -2 (para -3 <= Z < -2)
            # Nosso z_score_para_classificacao é o limite inferior da faixa que a criança atingiu.
            classificacao_rule = self.db.query(TabelaClassificacao).filter(
                TabelaClassificacao.indicador == indicador_map_key,
                TabelaClassificacao.idade_min_meses <= idade_total_meses,
                TabelaClassificacao.idade_max_meses >= idade_total_meses,
                (TabelaClassificacao.sexo_aplicavel == None) | (TabelaClassificacao.sexo_aplicavel == sexo_db.value),
                TabelaClassificacao.z_score_min <= z_score_para_classificacao,
                TabelaClassificacao.z_score_max > z_score_para_classificacao 
            ).first()

            if classificacao_rule:
                classificacao_str = classificacao_rule.classificacao_pt
                print(f"[SERVICE DEBUG] Classificação encontrada: {classificacao_str}")
            else:
                # Se z_score_para_classificacao for exatamente o limite superior de uma faixa (ex: Z=3.0)
                # e a regra for "Z >= 3.0", a condição z_score_max > z_score_para_classificacao pode falhar.
                # A TabelaClassificacao deve cobrir isso, ex, para Z>=3, z_score_max seria um valor muito alto.
                # Ex: Obesidade: min=3, max=999. Se z_score_para_classificacao=3.0, entra aqui.
                print(f"[SERVICE DEBUG] Nenhuma regra de classificação encontrada para Z-score pontual={z_score_para_classificacao}, ind={indicador_map_key}, idade={idade_total_meses}, sexo={sexo_db.value}")
                # Adicionar uma lógica de fallback ou verificação se a tabela de classificação está completa
                if z_score_para_classificacao == 3.0: # Caso especial para o limite superior +3Z
                    class_extremo_sup = self.db.query(TabelaClassificacao).filter(
                        TabelaClassificacao.indicador == indicador_map_key,
                        TabelaClassificacao.idade_min_meses <= idade_total_meses,
                        TabelaClassificacao.idade_max_meses >= idade_total_meses,
                        (TabelaClassificacao.sexo_aplicavel == None) | (TabelaClassificacao.sexo_aplicavel == sexo_db.value),
                        TabelaClassificacao.z_score_min == 3.0 # Regra para Z >= 3.0
                    ).first()
                    if class_extremo_sup:
                        classificacao_str = class_extremo_sup.classificacao_pt
                        print(f"[SERVICE DEBUG] Classificação de extremo superior encontrada: {classificacao_str}")

        z_final_arredondado = round(z_score_para_classificacao, 2) if z_score_para_classificacao is not None else None
        return z_final_arredondado, classificacao_str, faixa_z_desc

    def process_individual_data(self, data: IndividuoBase) -> ResultadoProcessamentoIndividual:
        anos, meses_componente, dias_componente, age_str, total_meses_completos, total_dias_vida = self.calculate_age_exact(data.data_nascimento, data.data_avaliacao)
        imc = self.calculate_imc(data.peso_kg, data.altura_cm)

        indicadores_calculados: List[IndicadorCalculado] = []
        
        try:
            sexo_db_val = SexoEnumDB(data.sexo.upper())
        except ValueError:
            # Lidar com valor de sexo inválido se o validator do Pydantic não pegar por algum motivo
            # ou se os dados vierem de outra fonte.
            raise ValueError(f"Valor de sexo inválido: {data.sexo}")

        map_indicadores_db = {
            "P/I": "peso_idade",
            "A/I": "estatura_idade", # No SISVAN, para <2 anos usa-se comprimento, >=2 anos altura.
                                    # As tabelas de referência OMS 0-5 anos já são "comprimento/estatura para idade".
                                    # Seus CSVs devem refletir isso. O indicador "estatura_idade" pode ser genérico.
            "IMC/I": "imc_idade"
        }

        # --- Peso-para-Idade (P/I) ---
        # Usado pelo SISVAN para crianças de 0 a <10 anos (ou seja, até 119 meses completos)
        if total_meses_completos < 120:
            z_pi, class_pi, faixa_pi_desc = self.get_z_score_range_and_classification(
                indicador_map_key=map_indicadores_db["P/I"],
                sexo_db=sexo_db_val,
                idade_total_meses=total_meses_completos,
                medida_valor=data.peso_kg
            )
            indicadores_calculados.append(IndicadorCalculado(
                tipo="Peso-para-Idade (P/I)",
                valor_medido=data.peso_kg,
                escore_z=z_pi, # Este é o Z-score do limite da faixa
                classificacao=class_pi,
                destaque=bool(class_pi and not any(s in class_pi.lower() for s in ["adequado", "eutro", "normal"])) # Ajuste as strings de "normal"
            ))
            print(f"[SERVICE DEBUG] P/I: Medida={data.peso_kg}, Z_classif={z_pi}, Classif='{class_pi}', Faixa='{faixa_pi_desc}'")

        # --- Altura-para-Idade (A/I) ---
        # Usado para 0 a 19 anos (0-228 meses)
        z_ai, class_ai, faixa_ai_desc = self.get_z_score_range_and_classification(
            indicador_map_key=map_indicadores_db["A/I"],
            sexo_db=sexo_db_val,
            idade_total_meses=total_meses_completos,
            medida_valor=data.altura_cm
        )
        indicadores_calculados.append(IndicadorCalculado(
            tipo="Altura-para-Idade (A/I)",
            valor_medido=data.altura_cm,
            escore_z=z_ai,
            classificacao=class_ai,
            destaque=bool(class_ai and "baixa estatura" in class_ai.lower()) # Destaque específico para baixa estatura
        ))
        print(f"[SERVICE DEBUG] A/I: Medida={data.altura_cm}, Z_classif={z_ai}, Classif='{class_ai}', Faixa='{faixa_ai_desc}'")

        # --- IMC-para-Idade (IMC/I) ---
        # Usado para 0 a 19 anos (0-228 meses)
        if imc is not None:
            z_imc, class_imc, faixa_imc_desc = self.get_z_score_range_and_classification(
                indicador_map_key=map_indicadores_db["IMC/I"],
                sexo_db=sexo_db_val,
                idade_total_meses=total_meses_completos,
                medida_valor=imc
            )
            indicadores_calculados.append(IndicadorCalculado(
                tipo="IMC-para-Idade (IMC/I)",
                valor_medido=imc,
                escore_z=z_imc,
                classificacao=class_imc,
                destaque=bool(class_imc and not any(s in class_imc.lower() for s in ["eutro", "normal"])) # Destaque para qualquer desvio da eutrofia
            ))
            print(f"[SERVICE DEBUG] IMC/I: Medida={imc}, Z_classif={z_imc}, Classif='{class_imc}', Faixa='{faixa_imc_desc}'")
        else:
            print("[SERVICE DEBUG] IMC não calculado (altura provavelmente zero).")


        return ResultadoProcessamentoIndividual(
            dados_entrada=data,
            idade_calculada_str=age_str,
            idade_anos=anos,
            idade_meses=meses_componente, # Retorna os meses do componente da idade
            idade_dias=dias_componente,   # Retorna os dias do componente da idade
            imc_calculado=imc,
            indicadores=indicadores_calculados
        )

    def process_batch_data(self, file_content: bytes, filename: str) -> List[ResultadoProcessamentoIndividual]:
        """
        Processa dados de um arquivo CSV/TSV em lote.
        Retorna uma lista de ResultadoProcessamentoIndividual.
        Lida com erros de formatação no arquivo e retorna resultados parciais.
        """
        import csv # Importar csv aqui para manter dependências do serviço mais limpas no topo
        import io

        resultados_finais: List[ResultadoProcessamentoIndividual] = []
        # TODO: Adicionar uma lista para armazenar erros de processamento por linha, se necessário.
        # erros_processamento: List[Dict] = []

        delimiter = ',' if filename.lower().endswith('.csv') else '\t'
        
        try:
            content_str = file_content.decode('utf-8-sig') # utf-8-sig lida com BOM opcional
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode('latin-1')
            except UnicodeDecodeError as e:
                # Se falhar, você pode querer lançar um erro que será pego pela API
                # ou retornar uma lista vazia com uma mensagem de erro em um campo especial.
                # Por enquanto, vamos lançar um ValueError.
                raise ValueError(f"Não foi possível decodificar o arquivo {filename}. Verifique a codificação (UTF-8 ou LATIN-1). Erro: {e}")

        file_like_object = io.StringIO(content_str)
        
        # Usar DictReader para facilitar o acesso às colunas pelo nome
        reader = csv.DictReader(file_like_object, delimiter=delimiter)
        
        # Normalizar nomes de cabeçalho (minúsculas, sem espaços extras)
        if reader.fieldnames:
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        else: # Arquivo vazio ou sem cabeçalho
            raise ValueError(f"Arquivo {filename} está vazio ou não contém cabeçalho.")


        # Definir os nomes esperados para as colunas (em minúsculas)
        # Esses nomes devem corresponder aos atributos do modelo Pydantic IndividuoBase
        expected_headers_map = {
            "nome": "nome", # Opcional
            "data_nascimento": "data_nascimento",
            "data_avaliacao": "data_avaliacao",
            "sexo": "sexo",
            "peso_kg": "peso_kg", # Ou "peso" se no CSV for só "peso"
            "altura_cm": "altura_cm"  # Ou "altura" se no CSV for só "altura"
        }
        required_csv_headers = ["data_nascimento", "data_avaliacao", "sexo", "peso_kg", "altura_cm"]

        # Verificar se os cabeçalhos obrigatórios estão presentes
        missing_headers = [csv_h for csv_h in required_csv_headers if csv_h not in reader.fieldnames]
        if missing_headers:
            raise ValueError(f"Cabeçalhos obrigatórios ausentes no arquivo {filename}: {', '.join(missing_headers)}. Encontrados: {', '.join(reader.fieldnames)}")

        for row_num, row_dict in enumerate(reader, start=2): # start=2 para considerar a linha do cabeçalho
            try:
                # Mapear dados da linha para os campos esperados pelo IndividuoBase
                individuo_data_dict = {}
                for pydantic_field, csv_header_key in expected_headers_map.items():
                    if csv_header_key in row_dict:
                        individuo_data_dict[pydantic_field] = row_dict[csv_header_key]
                    elif pydantic_field == "nome": # Nome é opcional
                        individuo_data_dict[pydantic_field] = None
                    # Não precisa de 'else' para campos obrigatórios pois já verificamos o cabeçalho

                # Validar e converter tipos com Pydantic
                # Garantir que campos numéricos sejam convertidos de string
                individuo_data_dict['peso_kg'] = float(str(individuo_data_dict['peso_kg']).replace(',', '.'))
                individuo_data_dict['altura_cm'] = float(str(individuo_data_dict['altura_cm']).replace(',', '.'))
                # Datas já devem ser strings no formato YYYY-MM-DD

                individuo_obj = IndividuoBase(**individuo_data_dict) # Validação Pydantic ocorre aqui
                
                resultado = self.process_individual_data(individuo_obj)
                resultados_finais.append(resultado)

            except ValueError as ve_pydantic: # Erros de validação Pydantic ou conversão de tipo
                print(f"Erro de validação/conversão na linha {row_num} do arquivo {filename}: {ve_pydantic} - Dados: {row_dict}")
                # Adicionar a uma lista de erros se quiser retornar informações sobre eles
                # erros_processamento.append({"linha": row_num, "erro": str(ve_pydantic), "dados": row_dict})
            except Exception as e_proc: # Outros erros durante o processamento da linha
                print(f"Erro inesperado ao processar linha {row_num} do arquivo {filename}: {e_proc} - Dados: {row_dict}")
                # erros_processamento.append({"linha": row_num, "erro": str(e_proc), "dados": row_dict})
        
        return resultados_finais