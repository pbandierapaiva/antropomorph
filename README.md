### Run Server
```powershell
ambiente/Scripts/activate
uvicorn app.main:app --reload
```

### 1. Visão Geral do Projeto

A Plataforma Antropométrica IC é uma aplicação web desenvolvida para realizar cálculos antropométricos com base em dados individuais ou em lote. Ela calcula indicadores como Peso-para-Idade (P/I), Altura-para-Idade (A/I) e IMC-para-Idade (IMC/I), fornecendo escores-Z e classificações nutricionais baseadas nas referências do SISVAN (Sistema de Vigilância Alimentar e Nutricional) e curvas da OMS.

**Funcionalidades Principais:**

*   **Processamento Individual:** Permite a entrada de dados de um único indivíduo (data de nascimento, data de avaliação, sexo, peso, altura) para obter os cálculos antropométricos.
*   **Processamento em Lote:** Permite o upload de um arquivo (CSV ou TSV) contendo dados de múltiplos indivíduos para processamento em massa.
*   **Cálculo de Idade:** Calcula a idade precisa em anos, meses e dias.
*   **Cálculo de IMC:** Calcula o Índice de Massa Corporal.
*   **Determinação de Escore-Z e Classificação:** Compara as medidas do indivíduo com tabelas de referência (OMS/SISVAN) para determinar o escore-Z e a classificação nutricional correspondente para cada indicador.
*   **Interface Web:** Fornece uma interface simples para interação do usuário.
*   **API RESTful:** Expõe endpoints para integração com outros sistemas.

### 2. Estrutura do Projeto

O projeto segue uma estrutura modular para facilitar a organização e manutenção:

```
projeto_ic_antropometria/
│
├── app/                      # Contém o código principal da aplicação FastAPI
│   ├── core/                 # Configurações centrais
│   │   └── config.py         # Configurações da aplicação (DB, app name, etc.)
│   ├── db/                   # Módulos relacionados ao banco de dados
│   │   ├── session.py        # Configuração da sessão SQLAlchemy e engine
│   │   └── base.py           # (Opcional, pode estar em session.py) Base para modelos SQLAlchemy
│   ├── models/               # Modelos Pydantic (validação de dados) e SQLAlchemy (ORM)
│   │   └── __init__.py       # (Exemplo, pode ser models.py) Definição dos modelos
│   ├── services/             # Lógica de negócio da aplicação
│   │   └── anthropometry_service.py # Serviço com os cálculos antropométricos
│   ├── static/               # Arquivos estáticos (CSS, JS, imagens)
│   │   └── css/
│   │       └── style.css     # (Exemplo)
│   ├── templates/            # Templates HTML (Jinja2)
│   │   └── index.html        # Página principal
│   └── main.py               # Ponto de entrada da aplicação FastAPI, define os endpoints
│
├── data/                     # Dados de referência (CSVs)
│   └── sisvan_tables/        # Tabelas de referência do SISVAN
│       ├── imci_m_0a59m.csv  # Exemplo de arquivo de dados
│       └── regras_classificacao_sisvan.csv # Exemplo de regras
│       └── ... (outros arquivos CSV)
│
├── scripts/                  # Scripts utilitários
│   └── populate_reference_data.py # Script para popular o BD com dados dos CSVs
│
├── ambiente/                 # (Opcional) Diretório do ambiente virtual Python
│
├── .env                      # (Opcional) Arquivo para variáveis de ambiente (não versionado)
├── requirements.txt          # Dependências do projeto Python
└── README.md                 # Documentação geral do projeto
```

### 3. Tecnologias Utilizadas

*   **Backend:**
    *   **Python 3.x**
    *   **FastAPI:** Framework web moderno e de alta performance para construir APIs.
    *   **Uvicorn:** Servidor ASGI para rodar a aplicação FastAPI.
    *   **SQLAlchemy:** ORM para interação com o banco de dados.
    *   **Pydantic:** Para validação de dados e gerenciamento de configurações.
    *   **python-dateutil:** Para cálculos de data e idade mais precisos.
    *   **PyMySQL:** Driver Python para conectar ao MariaDB/MySQL (especificado na `DATABASE_URL`).
*   **Banco de Dados:**
    *   **MariaDB (ou MySQL):** Sistema de gerenciamento de banco de dados relacional.
*   **Frontend (Básico):**
    *   **HTML5**
    *   **CSS3**
    *   **JavaScript (opcional, para interatividade no cliente)**
    *   **Jinja2:** Motor de templates para renderizar HTML no lado do servidor.
*   **Outros:**
    *   **CSV:** Formato para os arquivos de dados de referência e entrada em lote.

### 4. Configuração do Ambiente

1.  **Pré-requisitos:**
    *   Python 3.8 ou superior.
    *   MariaDB (ou MySQL) instalado e em execução.
    *   Um cliente de banco de dados (como DBeaver, HeidiSQL, ou o cliente de linha de comando `mysql`) para criar o banco de dados.

2.  **Criar Banco de Dados:**
    *   Crie um banco de dados no MariaDB/MySQL. Por exemplo, `antropometria_db` (conforme config.py).

3.  **Clonar o Repositório (se aplicável).**

4.  **Criar e Ativar Ambiente Virtual:**
    ```bash
    python -m venv ambiente
    ambiente\Scripts\activate  # Windows
    # source ambiente/bin/activate # Linux/macOS
    ```

5.  **Instalar Dependências:**
    Crie um arquivo requirements.txt com as seguintes dependências (no mínimo):
    ```txt
    # filepath: requirements.txt
    fastapi
    uvicorn[standard]
    sqlalchemy
    pydantic
    pydantic-settings
    python-dateutil
    pymysql  # Driver para MariaDB/MySQL
    jinja2
    # Adicione outras dependências se necessário
    ```
    Então, instale-as:
    ```bash
    pip install -r requirements.txt
    ```
    **Observação sobre o erro no terminal:** O erro `sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:mysql.mysqlclient` indica que o driver `mysqlclient` não foi encontrado. Embora sua string de conexão (`DATABASE_URL` em config.py) especifique `mysql+pymysql`, é crucial que `pymysql` esteja instalado no ambiente virtual. A inclusão de `pymysql` no requirements.txt e sua instalação resolvem este problema.

6.  **Configurar Variáveis de Ambiente (Opcional):**
    *   Crie um arquivo `.env` na raiz do projeto para sobrescrever as configurações padrão em config.py. Exemplo:
        ```env
        # filepath: .env
        DATABASE_URL="mysql+pymysql://seu_usuario:sua_senha@seu_host:3306/seu_banco_de_dados"
        DEBUG=True
        ```

### 5. Banco de Dados

#### 5.1. Configuração

A configuração da conexão com o banco de dados é gerenciada em config.py através da variável `DATABASE_URL`. O script session.py utiliza essa URL para criar a `engine` SQLAlchemy e fornecer sessões de banco de dados para a aplicação.

#### 5.2. Modelos SQLAlchemy (models.py)

Este arquivo (ou um módulo `app/models/`) define as tabelas do banco de dados como classes Python usando SQLAlchemy ORM. Os principais modelos são:

*   `TabelaReferenciaSISVAN`: Armazena os valores de referência (escores-Z) para os indicadores antropométricos (P/I, A/I, IMC/I) por sexo, idade em meses e os valores correspondentes para Z-scores (-3, -2, -1, 0, +1, +2, +3).
*   `TabelaClassificacao`: Armazena as regras de classificação nutricional baseadas no indicador, faixa etária, sexo (se aplicável) e faixas de escore-Z.

#### 5.3. Script de População de Dados (populate_reference_data.py)

Este script é responsável por:

1.  **Criar as Tabelas:** Executa `Base.metadata.create_all(bind=engine)` para criar as tabelas no banco de dados se elas não existirem.
2.  **Limpar Dados (Opcional):** Pode limpar os dados existentes das tabelas de referência antes de uma nova população.
3.  **Popular Tabelas:**
    *   Lê arquivos CSV localizados em sisvan_tables.
    *   Cada arquivo CSV contém dados de referência para um indicador específico, sexo e faixa etária (ex: imci_m_0a59m.csv para IMC/Idade, masculino, 0-59 meses).
    *   Os dados são processados e inseridos nas tabelas `TabelaReferenciaSISVAN` e `TabelaClassificacao`.
    *   O script mapeia os nomes dos arquivos e seus conteúdos para os campos corretos dos modelos SQLAlchemy.

**Para executar o script de população:**

```bash
(ambiente) PS D:\projeto_ic_antropometria> python scripts\populate_reference_data.py
```

### 6. API (FastAPI)

#### 6.1. Arquivo Principal (main.py)

Este é o coração da aplicação FastAPI. Ele define:

*   **Instância da Aplicação:** `app = FastAPI(...)`.
*   **Montagem de Arquivos Estáticos:** Serve arquivos CSS, JS da pasta static.
*   **Configuração de Templates Jinja2:** Para renderizar páginas HTML da pasta templates.
*   **Endpoints da API:**
    *   `GET /`: Serve a página HTML principal (`index.html`).
    *   `POST /api/processar/individual`: Recebe dados de um indivíduo no formato JSON, processa-os usando `AnthropometryService`, e retorna o resultado (`ResultadoProcessamentoIndividual`).
    *   `POST /api/processar/lote`: Recebe um arquivo (CSV ou TSV) via upload, processa cada linha usando `AnthropometryService`, e retorna uma lista de `ResultadoProcessamentoIndividual`.

#### 6.2. Modelos Pydantic (definidos em models.py)

FastAPI usa modelos Pydantic para validação de dados de requisição e serialização de respostas.

*   `IndividuoCreate` (ou `IndividuoBase`): Define a estrutura esperada para os dados de entrada de um indivíduo (nome, data de nascimento, data de avaliação, sexo, peso, altura).
*   `IndicadorCalculado`: Representa o resultado de um indicador específico (tipo, valor medido, escore-Z, classificação).
*   `ResultadoProcessamentoIndividual`: Define a estrutura da resposta para o processamento individual, incluindo os dados de entrada, idade calculada, IMC e uma lista de `IndicadorCalculado`.
*   `ResultadoProcessamentoLote` (opcional): Poderia ser usado para encapsular os resultados do processamento em lote, incluindo metadados como nome do arquivo, total processado, etc. Atualmente, o endpoint de lote retorna `List[ResultadoProcessamentoIndividual]`.

### 7. Lógica de Negócio (anthropometry_service.py)

A classe `AnthropometryService` encapsula toda a lógica de cálculo e avaliação antropométrica.

*   **`__init__(self, db: Session)`:** Recebe uma sessão SQLAlchemy para interagir com o banco de dados.
*   **`calculate_age_exact(dob, assessment_date)`:** Calcula a idade precisa em anos, meses, dias, total de meses e total de dias.
*   **`calculate_imc(peso_kg, altura_cm)`:** Calcula o IMC.
*   **`get_z_score_range_and_classification(indicador_map_key, sexo_db, idade_total_meses, medida_valor)`:**
    1.  Consulta a `TabelaReferenciaSISVAN` no banco de dados para obter os valores de referência (medidas para Z=-3 a Z=+3) para o indicador, sexo e idade fornecidos.
    2.  Determina em qual faixa de Z-score a `medida_valor` se encontra.
    3.  Usa um Z-score representativo (geralmente o limite inferior da faixa) para consultar a `TabelaClassificacao`.
    4.  Retorna o Z-score para classificação, a string de classificação e uma descrição da faixa Z.
*   **`process_individual_data(data: IndividuoBase)`:**
    1.  Calcula a idade e o IMC.
    2.  Para cada indicador relevante (P/I, A/I, IMC/I), chama `get_z_score_range_and_classification`.
    3.  Monta e retorna um objeto `ResultadoProcessamentoIndividual`.
*   **`process_batch_data(file_content: bytes, filename: str)`:**
    1.  Decodifica o conteúdo do arquivo (CSV ou TSV).
    2.  Usa `csv.DictReader` para ler as linhas do arquivo.
    3.  Valida os cabeçalhos do arquivo.
    4.  Para cada linha:
        *   Converte os dados para os tipos corretos.
        *   Cria um objeto `IndividuoBase` (ou similar).
        *   Chama `process_individual_data` para processar os dados do indivíduo.
        *   Coleta os resultados.
    5.  Retorna uma lista de `ResultadoProcessamentoIndividual`.
    6.  Inclui tratamento básico de erros por linha.

### 8. Interface do Usuário (Frontend)

A interface do usuário é simples e servida pelo FastAPI.

*   **index.html:** A página HTML principal, renderizada usando Jinja2. Provavelmente contém formulários para entrada de dados individuais e para upload de arquivos em lote.
*   **static:** Contém arquivos CSS (para estilização) e JavaScript (para interatividade no lado do cliente, se houver).

### 9. Como Executar o Projeto

1.  Certifique-se de que o ambiente está configurado (seção 4) e o banco de dados populado (seção 5.3).
2.  Ative o ambiente virtual:
    ```bash
    ambiente\Scripts\activate
    ```
3.  Execute o servidor Uvicorn a partir da raiz do projeto (projeto_ic_antropometria):
    ```bash
    uvicorn app.main:app --reload
    ```
    *   `app.main:app`: Indica ao Uvicorn para encontrar o objeto app no arquivo main.py.
    *   `--reload`: Faz o servidor reiniciar automaticamente quando houver alterações nos arquivos do projeto (útil para desenvolvimento).
4.  Acesse a aplicação no navegador, geralmente em `http://127.0.0.1:8000`.

### 10. Como Usar a API

*   **Endpoint de Processamento Individual:**
    *   **URL:** `POST /api/processar/individual`
    *   **Corpo da Requisição (JSON):**
        ```json
        {
          "nome": "João Exemplo", // Opcional
          "data_nascimento": "2022-01-15",
          "data_avaliacao": "2024-05-30",
          "sexo": "MASCULINO", // Ou "FEMININO"
          "peso_kg": 12.5,
          "altura_cm": 85.2
        }
        ```
    *   **Resposta (JSON):** Objeto `ResultadoProcessamentoIndividual`.

*   **Endpoint de Processamento em Lote:**
    *   **URL:** `POST /api/processar/lote`
    *   **Corpo da Requisição:** `multipart/form-data` contendo um arquivo (`file`). O arquivo deve ser CSV ou TSV com os seguintes cabeçalhos (exemplo, verificar anthropometry_service.py para os nomes exatos esperados):
        `data_nascimento,data_avaliacao,sexo,peso_kg,altura_cm,nome` (nome é opcional)
    *   **Resposta (JSON):** Lista de objetos `ResultadoProcessamentoIndividual`.

### 11. Observações e Pontos de Melhoria

*   **Tratamento de Erros:** O tratamento de erros pode ser aprimorado, especialmente no processamento em lote, para fornecer feedback mais detalhado sobre quais linhas falharam e por quê.
*   **Segurança:** Para produção, considerar aspectos de segurança como HTTPS, autenticação/autorização se necessário, e validação de entrada mais robusta.
*   **Testes:** Implementar testes unitários e de integração para garantir a corretude dos cálculos e o funcionamento dos endpoints.
*   **Logging:** Implementar um sistema de logging mais robusto em vez de `print()` para depuração e monitoramento.
*   **Documentação da API:** FastAPI gera documentação interativa automaticamente (Swagger UI em `/docs` e ReDoc em `/redoc`), o que é uma grande vantagem.
*   **Tabelas de Referência:** O sistema depende da correta população das tabelas de referência. Garantir que os arquivos CSV estejam corretos e completos é crucial.
*   **Interpolação:** O método `get_z_score_range_and_classification` atual não interpola para calcular um escore-Z fracionado exato, mas sim identifica a faixa e usa o limite inferior para classificação. Dependendo da precisão desejada, a interpolação linear poderia ser implementada.
*   **Frontend:** A interface do usuário atual é básica. Poderia ser aprimorada com um framework JavaScript moderno (Vue, React, Angular) para uma experiência mais rica e interativa.
