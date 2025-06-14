import csv
import os
import sys
from sqlalchemy.orm import Session

# Adiciona o diretório raiz do projeto ao sys.path para permitir importações de 'app'
# Isso é útil se você executar este script da pasta 'scripts/' ou de qualquer outro lugar.
# Se executar da raiz do projeto (onde está 'app/'), isso pode não ser estritamente necessário
# mas não faz mal.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal, engine, Base
from app.models import TabelaReferenciaSISVAN, TabelaClassificacao, SexoEnumDB

# Diretório onde os arquivos CSV de dados estão localizados
# Assume que este script (populate_reference_data.py) está na pasta 'scripts'
# e os CSVs estão em 'data/sisvan_tables/'
# ../data/sisvan_tables/
BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'sisvan_tables'))

def create_db_and_tables():
    """Cria todas as tabelas no banco de dados definidas em Base.metadata."""
    print("Verificando e criando tabelas (se não existirem)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        raise

def clear_table_data(db: Session, table_class):
    """Remove todos os dados de uma tabela específica."""
    table_name = table_class.__tablename__
    print(f"Limpando dados da tabela {table_name}...")
    try:
        num_deleted = db.query(table_class).delete()
        db.commit()
        print(f"{num_deleted} registros deletados da tabela {table_name}.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao limpar dados da tabela {table_name}: {e}")
        raise

def populate_tabela_referencia_sisvan(db: Session, csv_filename: str, indicador: str, sexo_enum: SexoEnumDB, idade_inicial_meses: int):
    """
    Popula a TabelaReferenciaSISVAN com dados de um CSV específico.
    O CSV deve ter o cabeçalho '-3,-2,-1,0,1,2,3' e cada linha subsequente
    representa uma idade em meses, começando de idade_inicial_meses.
    """
    filepath = os.path.join(BASE_DATA_DIR, csv_filename)
    if not os.path.exists(filepath):
        print(f"AVISO: Arquivo {filepath} não encontrado. Pulando população para este arquivo.")
        return

    print(f"Populando TabelaReferenciaSISVAN com '{csv_filename}' para {indicador}, sexo {sexo_enum.value}, começando da idade {idade_inicial_meses} meses...")
    
    current_age_meses = idade_inicial_meses
    count_inserted = 0
    count_skipped_malformed = 0
    count_skipped_exists = 0

    # Nomes dos campos no modelo TabelaReferenciaSISVAN para os valores Z
    z_value_field_names = [
        'valor_z_neg_3', 'valor_z_neg_2', 'valor_z_neg_1', 'valor_z_0',
        'valor_z_pos_1', 'valor_z_pos_2', 'valor_z_pos_3'
    ]
    num_z_columns = len(z_value_field_names)

    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as csvfile: # utf-8-sig para lidar com BOM
            reader = csv.reader(csvfile)
            
            # Pular o cabeçalho
            try:
                header = next(reader)
                expected_header = ['-3','-2','-1','0','1','2','3'] # Como as colunas devem ser
                if [h.strip() for h in header] != expected_header:
                    print(f"AVISO: Cabeçalho inesperado em '{csv_filename}': {header}. Esperado: {expected_header}. Tentando prosseguir.")
            except StopIteration:
                print(f"ERRO: Arquivo '{csv_filename}' está vazio ou não tem cabeçalho.")
                return

            for row_index, row_values in enumerate(reader):
                if len(row_values) != num_z_columns:
                    print(f"AVISO: Linha {row_index + 2} em '{csv_filename}' tem {len(row_values)} colunas, esperado {num_z_columns}. Pulando linha: {row_values}")
                    count_skipped_malformed +=1
                    current_age_meses += 1 # Ainda avança a idade se a linha é apenas malformada
                    continue

                data_for_model = {
                    "indicador": indicador,
                    "sexo": sexo_enum,
                    "idade_meses": current_age_meses
                }
                
                valid_row = True
                for i, field_name in enumerate(z_value_field_names):
                    try:
                        value_str = row_values[i].strip().replace(',', '.') # Substitui vírgula por ponto para float
                        if value_str:
                            data_for_model[field_name] = float(value_str)
                        else:
                            data_for_model[field_name] = None
                    except ValueError:
                        print(f"AVISO: Valor float inválido '{row_values[i]}' para {field_name} na linha {row_index + 2} de '{csv_filename}'. Pulando linha.")
                        valid_row = False
                        break 
                
                if not valid_row:
                    count_skipped_malformed +=1
                    current_age_meses += 1
                    continue

                # Verificar se já existe um registro para evitar UniqueConstraintError
                exists = db.query(TabelaReferenciaSISVAN.id).filter_by(
                    indicador=indicador, sexo=sexo_enum, idade_meses=current_age_meses
                ).scalar() is not None # .scalar() is not None é mais eficiente que .first() para checar existência

                if not exists:
                    try:
                        ref_data = TabelaReferenciaSISVAN(**data_for_model)
                        db.add(ref_data)
                        count_inserted += 1
                    except Exception as e: # Captura exceções mais amplas durante a criação do objeto ou add
                        print(f"Erro ao criar/adicionar objeto TabelaReferenciaSISVAN para linha {row_index + 2} ({current_age_meses} meses): {data_for_model} - Erro: {e}")
                        count_skipped_malformed +=1 # Conta como malformado se a criação do objeto falhar
                else:
                    count_skipped_exists +=1
                
                current_age_meses += 1
        
        db.commit()
        print(f"Concluído para '{csv_filename}': {count_inserted} registros inseridos, "
              f"{count_skipped_malformed} linhas malformadas puladas, "
              f"{count_skipped_exists} registros duplicados (já existentes) pulados.")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filepath}' não encontrado.")
    except Exception as e:
        db.rollback()
        print(f"ERRO GERAL ao processar '{csv_filename}': {e}")
        raise

def populate_tabela_classificacao(db: Session, csv_filename: str):
    """Popula a TabelaClassificacao com dados de um CSV."""
    filepath = os.path.join(BASE_DATA_DIR, csv_filename)
    if not os.path.exists(filepath):
        print(f"AVISO: Arquivo de classificação {filepath} não encontrado. Pulando.")
        return

    print(f"Populando TabelaClassificacao com dados de '{csv_filename}'...")
    count_inserted = 0
    count_skipped_malformed = 0
    count_skipped_exists = 0

    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as csvfile:
            # Usar DictReader para facilitar o acesso às colunas pelo nome do cabeçalho
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames or not all(f in reader.fieldnames for f in ['indicador', 'idade_min_meses', 'idade_max_meses', 'z_score_min', 'z_score_max', 'classificacao_pt']):
                print(f"ERRO: Cabeçalho inválido ou ausente no arquivo de classificação '{csv_filename}'. Colunas esperadas incluem: 'indicador', 'idade_min_meses', etc.")
                return

            for row_index, row in enumerate(reader):
                try:
                    # sexo_aplicavel é opcional no CSV; se ausente ou vazio, será None
                    sexo_str = row.get('sexo_aplicavel', '').strip().upper()
                    sexo_val = sexo_str if sexo_str in ['M', 'F'] else None

                    # Verificar duplicidade (UniqueConstraint não foi definido para esta tabela no modelo, mas é bom checar)
                    # Se você definir um UniqueConstraint no modelo TabelaClassificacao, esta checagem pode ser removida
                    # e o try-except em db.add() lidaria com isso.
                    # Para este exemplo, vamos pular a checagem de existência aqui e confiar na limpeza prévia se necessário.

                    class_rule = TabelaClassificacao(
                        indicador=row['indicador'].strip(),
                        idade_min_meses=int(row['idade_min_meses'].strip()),
                        idade_max_meses=int(row['idade_max_meses'].strip()),
                        sexo_aplicavel=sexo_val,
                        z_score_min=float(row['z_score_min'].strip().replace(',', '.')),
                        z_score_max=float(row['z_score_max'].strip().replace(',', '.')),
                        classificacao_pt=row['classificacao_pt'].strip()
                    )
                    db.add(class_rule)
                    count_inserted += 1
                except KeyError as ke:
                    print(f"AVISO: Coluna ausente na linha {row_index + 2} de '{csv_filename}'. Erro: {ke}. Linha: {row}")
                    count_skipped_malformed +=1
                except ValueError as ve:
                    print(f"AVISO: Valor inválido na linha {row_index + 2} de '{csv_filename}'. Erro: {ve}. Linha: {row}")
                    count_skipped_malformed +=1
                except Exception as e: # Outras exceções
                    print(f"ERRO ao processar linha {row_index + 2} de '{csv_filename}': {e}. Linha: {row}")
                    count_skipped_malformed +=1
        
        db.commit()
        print(f"Concluído para '{csv_filename}': {count_inserted} regras de classificação inseridas, "
              f"{count_skipped_malformed} linhas malformadas puladas.")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filepath}' não encontrado.")
    except Exception as e:
        db.rollback()
        print(f"ERRO GERAL ao processar '{csv_filename}': {e}")
        raise

if __name__ == "__main__":
    print(f"Usando diretório de dados: {BASE_DATA_DIR}")
    
    # 1. Garanta que o banco de dados (ex: 'antropometria_db') exista no MariaDB.
    # Este script NÃO cria o banco de dados em si, apenas as tabelas dentro dele.
    
    # 2. Crie as tabelas no banco de dados com base nos modelos SQLAlchemy
    # Isso é seguro de executar múltiplas vezes; não recriará tabelas existentes.
    try:
        create_db_and_tables()
    except Exception:
        print("Falha ao criar tabelas. Saindo.")
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        # 3. Opcional: Limpar dados das tabelas antes de popular novamente
        # Descomente se quiser recarregar tudo do zero.
        # clear_table_data(db, TabelaReferenciaSISVAN)
        # clear_table_data(db, TabelaClassificacao)
        # print("Todas as tabelas de referência foram limpas.")

        # 4. Popule a TabelaReferenciaSISVAN (valores Z)
        print("\n--- Iniciando população da TabelaReferenciaSISVAN ---")
        # PESO-PARA-IDADE (pi)
        # 0-59 meses (0 a <5 anos)
        populate_tabela_referencia_sisvan(db, "pi_m_0a59m.csv",    "peso_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=0)
        populate_tabela_referencia_sisvan(db, "pi_f_0a59m.csv",    "peso_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=0)
        # 60-119 meses (5 a <10 anos) - SISVAN usa P/I até <10 anos
        populate_tabela_referencia_sisvan(db, "pi_m_60a119m.csv",  "peso_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=60)
        populate_tabela_referencia_sisvan(db, "pi_f_60a119m.csv",  "peso_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=60)

        # ESTATURA-PARA-IDADE (ei)
        # 0-59 meses (0 a <5 anos)
        populate_tabela_referencia_sisvan(db, "ei_m_0a59m.csv",    "estatura_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=0)
        populate_tabela_referencia_sisvan(db, "ei_f_0a59m.csv",    "estatura_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=0)
        # 60-228 meses (5 a 19 anos) - Idade 228 é 19 anos e 0 meses.
        # Se for "até 18 anos e 11 meses", a última idade é 227. Ajuste o nome do arquivo e a chamada.
        populate_tabela_referencia_sisvan(db, "ei_m_60a228m.csv",  "estatura_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=60)
        populate_tabela_referencia_sisvan(db, "ei_f_60a228m.csv",  "estatura_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=60)

        # IMC-PARA-IDADE (imci)
        # 0-59 meses (0 a <5 anos)
        populate_tabela_referencia_sisvan(db, "imci_m_0a59m.csv",  "imc_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=0)
        populate_tabela_referencia_sisvan(db, "imci_f_0a59m.csv",  "imc_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=0)
        # 60-228 meses (5 a 19 anos)
        populate_tabela_referencia_sisvan(db, "imci_m_60a228m.csv","imc_idade", SexoEnumDB.MASCULINO, idade_inicial_meses=60)
        populate_tabela_referencia_sisvan(db, "imci_f_60a228m.csv","imc_idade", SexoEnumDB.FEMININO,  idade_inicial_meses=60)
        
        print("--- População da TabelaReferenciaSISVAN concluída ---")

        # 5. Popule a TabelaClassificacao
        print("\n--- Iniciando população da TabelaClassificacao ---")
        populate_tabela_classificacao(db, "regras_classificacao_sisvan.csv")
        print("--- População da TabelaClassificacao concluída ---")

        print("\nPopulação de todos os dados de referência concluída com sucesso!")

    except Exception as e:
        print(f"UM ERRO GERAL OCORREU DURANTE A POPULAÇÃO: {e}")
        # db.rollback() # O rollback já deve ser feito dentro das funções se ocorrer erro lá
    finally:
        db.close()
        print("Sessão do banco de dados fechada.")