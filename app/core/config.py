from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Plataforma Antropométrica IC"
    DEBUG: bool = True

    # Configurações do Banco de Dados MariaDB
    # Substitua com suas credenciais e detalhes do MariaDB
    # Exemplo: "mysql+mysqlclient://user:password@host:port/dbname"
    DATABASE_URL: Optional[str] = "mysql+pymysql://root:mel03097015@localhost:3306/antropometria_db"

    # SISVAN reference tables - nomes das tabelas que você criará
    # Estes são exemplos, você precisará definir os nomes corretos
    SISVAN_TABLE_WHO_0_5_REF: str = "sisvan_ref_who_0_5_anos" # Ex: Peso/Idade, Altura/Idade, IMC/Idade para 0-5 anos
    SISVAN_TABLE_WHO_5_19_REF: str = "sisvan_ref_who_5_19_anos" # Ex: IMC/Idade, Altura/Idade para 5-19 anos
    SISVAN_CLASSIFICATION_RULES: str = "sisvan_classification_rules" # Tabela com regras de classificação

    class Config:
        env_file = ".env" # Se você quiser usar um arquivo .env para variáveis de ambiente
        env_file_encoding = 'utf-8'

settings = Settings()

# Para testar se está carregando:
if __name__ == "__main__":
    print(f"App Name: {settings.APP_NAME}")
    print(f"Database URL: {settings.DATABASE_URL}")
    if not settings.DATABASE_URL:
        print("AVISO: DATABASE_URL não está configurada. Verifique seu arquivo .env ou as configurações.")
