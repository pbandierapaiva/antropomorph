# app/services/anthropometry_service.py

import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.models import (
    IndividuoCreate,
    ResultadoProcessamentoIndividual,
    Indicador,
    ErroLinha,
    TabelaReferenciaSISVAN,
    TabelaClassificacao,
    SexoEnum
)

def get_reference_value(db: Session, table_name: str, age_in_months: int, gender: str) -> Optional[TabelaReferenciaSISVAN]:
    indicador_map = {'pi_m': 'peso_idade', 'pi_f': 'peso_idade','ei_m': 'estatura_idade', 'ei_f': 'estatura_idade', 'imci_m': 'imc_idade', 'imci_f': 'imc_idade'}
    db_indicator_name = indicador_map.get(table_name)
    if not db_indicator_name: return None
    sexo_map = {'M': 'M', 'F': 'F'}
    db_gender = sexo_map.get(gender.upper())
    if not db_gender: return None
    return db.query(TabelaReferenciaSISVAN).filter(TabelaReferenciaSISVAN.indicador == db_indicator_name, TabelaReferenciaSISVAN.sexo == db_gender, TabelaReferenciaSISVAN.idade_meses == age_in_months).first()

def get_classification_rule(db: Session, table_name: str, age_in_months: int, z_score: float) -> Optional[str]:
    indicador_map = {'pi_m': 'peso_idade', 'pi_f': 'peso_idade', 'ei_m': 'estatura_idade', 'ei_f': 'estatura_idade','imci_m': 'imc_idade', 'imci_f': 'imc_idade'}
    db_indicator_name = indicador_map.get(table_name)
    if not db_indicator_name: return "Indicador desconhecido"
    rule = db.query(TabelaClassificacao).filter(TabelaClassificacao.indicador == db_indicator_name, TabelaClassificacao.idade_min_meses <= age_in_months, TabelaClassificacao.idade_max_meses >= age_in_months, TabelaClassificacao.z_score_min < z_score, TabelaClassificacao.z_score_max >= z_score).first()
    return str(rule.classificacao) if rule else "Classificação não encontrada"

class AnthropometryService:
    def __init__(self, db: Optional[Session]):
        self.db = db

    def calculate_age_exact(self, birth_date: date, evaluation_date: date) -> Tuple[int, int, int, str, int, int]:
        """
        Calcula idade exata em anos, meses e dias, retornando também
        o total em meses e total em dias
        """
        if evaluation_date < birth_date:
            raise ValueError("Data de avaliação não pode ser anterior ao nascimento.")
        
        delta = relativedelta(evaluation_date, birth_date)
        total_months = delta.years * 12 + delta.months
        total_days = (evaluation_date - birth_date).days
        
        # Formato da string de idade
        age_str_parts = []
        if delta.years > 0:
            age_str_parts.append(f"{delta.years} ano{'s' if delta.years > 1 else ''}")
        if delta.months > 0:
            age_str_parts.append(f"{delta.months} {'meses' if delta.months > 1 else 'mês'}")
        if not age_str_parts and delta.days > 0:
            age_str_parts.append(f"{delta.days} dias")
        
        age_str = " e ".join(age_str_parts) if age_str_parts else "0 dias"
        
        return (delta.years, delta.months, delta.days, age_str, total_months, total_days)

    def calculate_imc(self, peso_kg: float, altura_cm: float) -> Optional[float]:
        """
        Calcula o IMC (Índice de Massa Corporal)
        """
        if altura_cm <= 0:
            return None
        
        altura_m = altura_cm / 100
        imc = peso_kg / (altura_m * altura_m)
        return round(imc, 2)

    def _calculate_age(self, birth_date: date, evaluation_date: date) -> Tuple[int, str]:
        if evaluation_date < birth_date:
            raise ValueError("Data de avaliação não pode ser anterior ao nascimento.")
        
        delta = relativedelta(evaluation_date, birth_date)
        age_in_months = delta.years * 12 + delta.months
        
        age_str_parts = []
        if delta.years > 0: 
            age_str_parts.append(f"{delta.years} ano{'s' if delta.years > 1 else ''}")
        if delta.months > 0: 
            age_str_parts.append(f"{delta.months} {'meses' if delta.months > 1 else 'mês'}")
        
        if not age_str_parts: 
            return 0, "0 meses"
        return age_in_months, " e ".join(age_str_parts)

    def _interpolate_z_score(self, value: Decimal, ref_row: TabelaReferenciaSISVAN) -> Optional[float]:
        z_scores = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        ref_values = [getattr(ref_row, f'valor_z_{"neg" if z < 0 else "pos"}_{abs(int(z))}' if z != 0 else 'valor_z_0') for z in z_scores]
        ref_values_decimal = [Decimal(str(v)) if v is not None else None for v in ref_values]
        
        for i in range(len(ref_values_decimal) - 1):
            lower_bound, upper_bound = ref_values_decimal[i], ref_values_decimal[i+1]
            if lower_bound is not None and upper_bound is not None and lower_bound <= value <= upper_bound:
                z_lower, z_upper = z_scores[i], z_scores[i+1]
                range_ref = upper_bound - lower_bound
                if range_ref == 0: 
                    return z_lower
                proportion = (value - lower_bound) / range_ref
                return z_lower + float(proportion) * (z_upper - z_lower)
        
        if ref_values_decimal[0] is not None and value < ref_values_decimal[0]: 
            return -3.1
        if ref_values_decimal[-1] is not None and value > ref_values_decimal[-1]: 
            return 3.1
        return None

    def _get_indicator(self, table_name: str, age_in_months: int, value: Decimal, gender: str) -> Optional[Indicador]:
        if self.db is None:
            # Para testes sem DB, retorna um indicador placeholder
            return Indicador(
                tipo=f"Teste-{table_name}",
                valor_observado=value,
                escore_z=0.0,
                classificacao="Teste - Sem DB"
            )
        
        ref = get_reference_value(self.db, table_name, age_in_months, gender)
        if not ref: return None
        z_score = self._interpolate_z_score(value, ref)
        if z_score is None: return None
        
        classification = get_classification_rule(self.db, table_name, age_in_months, z_score)
        indicador_display_map = {"pi": "Peso-para-Idade (P/I)", "ei": "Altura-para-Idade (A/I)", "imci": "IMC-para-Idade (IMC/I)"}
        display_name = indicador_display_map.get(table_name.split('_')[0], table_name)
        
        return Indicador(tipo=display_name, valor_observado=value, escore_z=round(z_score, 2), classificacao=classification or "Não aplicável")

    def process_individual_data(self, data: IndividuoCreate) -> ResultadoProcessamentoIndividual:
        age_in_months, age_str = self._calculate_age(data.data_nascimento, data.data_avaliacao)
        indicadores: List[Indicador] = []
        
        if age_in_months <= 120:
            p_i = self._get_indicator(f"pi_{data.sexo.value.lower()}", age_in_months, data.peso_kg, data.sexo.value)
            if p_i: indicadores.append(p_i)
        if age_in_months <= 228:
            a_i = self._get_indicator(f"ei_{data.sexo.value.lower()}", age_in_months, data.altura_cm, data.sexo.value)
            if a_i: indicadores.append(a_i)
            
        imc_decimal: Optional[Decimal] = None
        if data.altura_cm > 0:
            altura_m = data.altura_cm / Decimal(100)
            imc_decimal = data.peso_kg / (altura_m * altura_m)
            if age_in_months <= 228:
                imc_i = self._get_indicator(f"imci_{data.sexo.value.lower()}", age_in_months, imc_decimal, data.sexo.value)
                if imc_i: indicadores.append(imc_i)
        
        return ResultadoProcessamentoIndividual(
            id_paciente=data.id_paciente,
            nome=data.nome,
            sexo=data.sexo.name.capitalize(),
            data_nascimento=data.data_nascimento,
            data_avaliacao=data.data_avaliacao,
            idade=age_str,
            peso_kg=data.peso_kg,
            altura_cm=data.altura_cm,
            imc=float(round(imc_decimal, 2)) if imc_decimal is not None else None,
            indicadores=indicadores
        )

    def _parse_date_flexible(self, date_str: str) -> date:
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try: 
                return datetime.strptime(date_str, fmt).date()
            except (ValueError, TypeError): 
                continue
        raise ValueError(f"Formato de data inválido: '{date_str}'. Use AAAA-MM-DD ou DD/MM/AAAA.")

    def _parse_float_flexible(self, value_str: str) -> Decimal:
        try: 
            # Remove espaços e normaliza separadores decimais
            normalized = str(value_str).strip().replace(',', '.')
            # Remove aspas se existirem
            normalized = normalized.strip('"').strip("'")
            return Decimal(normalized)
        except (InvalidOperation, TypeError): 
            raise ValueError(f"Valor numérico inválido: '{value_str}'.")

    def _parse_sex_flexible(self, sex_str: str) -> SexoEnum:
        """Converte valores flexíveis de sexo para SexoEnum"""
        if not sex_str:
            raise ValueError("Sexo é obrigatório")
        
        sex_normalized = str(sex_str).strip().upper()
        
        # Mapeamentos flexíveis
        male_values = ['M', 'MASCULINO', 'MALE', 'HOMEM', 'MACHO']
        female_values = ['F', 'FEMININO', 'FEMALE', 'MULHER', 'FEMEA']
        
        if sex_normalized in male_values:
            return SexoEnum.M
        elif sex_normalized in female_values:
            return SexoEnum.F
        else:
            raise ValueError(f"Valor de sexo inválido: '{sex_str}'. Use M/F, Masculino/Feminino, etc.")

    def _normalize_header(self, header: str) -> str:
        """Normaliza headers para matching flexível"""
        if not header:
            return ""
        
        # Remove espaços, converte para minúsculas e remove caracteres especiais
        normalized = header.strip().lower()
        normalized = normalized.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        
        # Mapeamentos específicos
        header_mappings = {
            'id': 'id_paciente',
            'identificacao': 'id_paciente',
            'id_paciente': 'id_paciente',
            'sus': 'id_paciente',
            'cpf': 'id_paciente',
            'cartao_sus': 'id_paciente',
            'numero_sus': 'id_paciente',
            'nome_completo': 'nome',
            'data_de_nascimento': 'data_nascimento',
            'data_da_avaliacao': 'data_avaliacao',
            'data_avaliacao': 'data_avaliacao',
            'gender': 'sexo',
            'peso_kg': 'peso_kg',
            'peso__kg_': 'peso_kg',
            'altura_cm': 'altura_cm',
            'altura__cm_': 'altura_cm'
        }
        
        return header_mappings.get(normalized, normalized)
    def process_batch_data(self, file_contents: bytes, filename: str) -> Dict[str, Any]:
        # Validação de arquivo vazio
        if not file_contents:
            raise ValueError("Arquivo está vazio")
        
        try: 
            decoded_content = file_contents.decode('utf-8-sig')  # Remove BOM se existir
        except UnicodeDecodeError: 
            try:
                decoded_content = file_contents.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError("Não foi possível decodificar o arquivo. Verifique se ele está no formato UTF-8.")

        # Validação de conteúdo vazio após decodificação
        if not decoded_content.strip():
            raise ValueError("Arquivo não contém dados válidos")

        # Determinar delimitador
        sniffer = csv.Sniffer()
        try:
            sample_lines = decoded_content.splitlines()[:3]  # Pega as primeiras 3 linhas
            if sample_lines:
                dialect = sniffer.sniff('\n'.join(sample_lines))
                delimiter = dialect.delimiter
            else:
                raise ValueError("Arquivo não contém linhas válidas")
        except csv.Error:
            delimiter = ',' if filename.endswith('.csv') else '\t'
        
        # Processar CSV
        reader = csv.DictReader(io.StringIO(decoded_content), delimiter=delimiter)
        
        # Validar headers obrigatórios
        required_headers = {'data_nascimento', 'data_avaliacao', 'sexo', 'peso_kg', 'altura_cm'}
        normalized_headers = {self._normalize_header(header): header for header in reader.fieldnames or []}
        
        missing_headers = required_headers - set(normalized_headers.keys())
        if missing_headers:
            raise ValueError(f"Headers obrigatórios não encontrados: {', '.join(missing_headers)}")
        
        resultados_individuais, erros_por_linha = [], []
        total_rows_attempted = 0
        
        for i, row in enumerate(reader):
            line_number = i + 2  # +2 porque começamos da linha 2 (linha 1 é o header)
            total_rows_attempted += 1
            
            try:
                # Normalizar as chaves do row
                normalized_row = {}
                for header, value in row.items():
                    normalized_key = self._normalize_header(header)
                    normalized_row[normalized_key] = value.strip() if value else ''
                
                # Validar campos obrigatórios (exceto nome que é opcional)
                for field in required_headers:
                    if not normalized_row.get(field):
                        raise ValueError(f"{field} é obrigatório")
                
                # Criar IndividuoCreate
                individuo_data = IndividuoCreate(
                    id_paciente=normalized_row.get('id_paciente', '').strip() or None,  # Opcional
                    nome=normalized_row.get('nome', f'Pessoa {line_number-1}'),  # Nome padrão se não informado
                    data_nascimento=self._parse_date_flexible(normalized_row['data_nascimento']),
                    data_avaliacao=self._parse_date_flexible(normalized_row['data_avaliacao']),
                    sexo=self._parse_sex_flexible(normalized_row['sexo']),
                    peso_kg=self._parse_float_flexible(normalized_row['peso_kg']),
                    altura_cm=self._parse_float_flexible(normalized_row['altura_cm'])
                )
                
                resultado = self.process_individual_data(individuo_data)
                resultados_individuais.append(resultado)

            except Exception as e:
                erros_por_linha.append(ErroLinha(linha=line_number, erro=str(e), dados_originais=row))
        
        return {
            "resultados_individuais": resultados_individuais, 
            "erros_por_linha": erros_por_linha,
            "total_rows_attempted": total_rows_attempted
        }