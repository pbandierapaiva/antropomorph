# 🏥 Sistema de Avaliação Antropométrica

> **Projeto de Iniciação Científica - LABDIS UNIFESP**  
> **Desenvolvido por:** João Paulo Oliveira Braga  
> **Orientadores:** 
> -  **Prof Dr. Paulo Bandiera Paiva** – Professor associado
> -  **Profa Dra. Andréia Cascaes Cruz** – Professora adjunta
> 
> **Desenvolvido em:** LABDIS - Laboratório de Desenvolvimento e Inovação em Saúde

## 🚀 Início Rápido

### Executar Servidor
```powershell
# Ativar ambiente virtual
ambiente/Scripts/activate

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Acessar Aplicação
- **Interface Web:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs
- **API Alternativa:** http://localhost:8000/redoc

---

## 📋 Visão Geral

O **Sistema de Avaliação Antropométrica** é uma aplicação web moderna desenvolvida para realizar análises antropométricas precisas com base nas diretrizes do SISVAN (Sistema de Vigilância Alimentar e Nutricional) e curvas de crescimento da OMS.

### ✨ Funcionalidades Principais

- 🧑‍⚕️ **Avaliação Individual**: Processamento individual com interface intuitiva
- 📊 **Avaliação em Lote**: Upload e processamento de arquivos CSV/TSV
- 📈 **Dashboard Inteligente**: Estatísticas em tempo real e atividades recentes
- 📋 **Relatórios em PDF**: Exportação profissional de resultados
- 🎯 **Indicadores Completos**: P/I, A/I, IMC/I com classificações nutricionais
- 📱 **Interface Responsiva**: Design moderno adaptável a todos os dispositivos

### 🏆 Diferenciais

- ✅ **Tabelas padronizadas** em todas as seções
- ✅ **Badges coloridos** para classificações nutricionais
- ✅ **Cálculo preciso de idade** (anos, meses e dias)
- ✅ **Interface moderna** com Tailwind CSS e Lucide Icons
- ✅ **API RESTful** para integração com outros sistemas
- ✅ **Validação robusta** de dados de entrada

---

## 🏗️ Arquitetura do Sistema

### 📁 Estrutura do Projeto

```
projeto_ic_antropometria/
│
├── 🚀 app/                          # Aplicação principal FastAPI
│   ├── 🔧 core/                     # Configurações centrais
│   │   └── config.py                # Configurações da aplicação
│   ├── 🗄️ db/                       # Módulos de banco de dados
│   │   └── session.py               # Configuração SQLAlchemy
│   ├── 📊 services/                 # Lógica de negócio
│   │   └── anthropometry_service.py # Serviços antropométricos
│   ├── 🎨 static/                   # Arquivos estáticos
│   │   ├── css/style.css            # Estilos CSS
│   │   ├── js/script.js             # JavaScript
│   │   └── modelo/                  # Modelos de importação
│   ├── 📝 templates/                # Templates HTML
│   │   └── index.html               # Interface principal
│   ├── 📋 models.py                 # Modelos Pydantic/SQLAlchemy  
│   ├── 📐 schemas.py                # Esquemas de validação
│   └── 🌐 main.py                   # Ponto de entrada FastAPI
│
├── 📊 data/                         # Dados de referência
│   └── sisvan_tables/               # Tabelas SISVAN/OMS
│       ├── ei_*.csv                 # Estatura/Idade por sexo/idade
│       ├── imci_*.csv               # IMC/Idade por sexo/idade  
│       ├── pi_*.csv                 # Peso/Idade por sexo/idade
│       └── regras_classificacao_sisvan.csv
│
├── 🛠️ scripts/                      # Scripts utilitários
│   └── populate_reference_data.py   # Popular dados de referência
│
├── 🧪 tests/                        # Testes automatizados
│   ├── test_anthropometry_service.py
│   ├── test_api.py
│   └── test_app.py
│
├── 🌍 ambiente/                     # Ambiente virtual Python
├── 📋 requirements.txt              # Dependências do projeto
└── 📖 README.MD                     # Esta documentação
```

### 🛠️ Tecnologias Utilizadas

#### Backend
- **🐍 Python 3.8+** - Linguagem principal
- **⚡ FastAPI** - Framework web moderno e performático
- **🦄 Uvicorn** - Servidor ASGI de alta performance
- **🗃️ SQLAlchemy** - ORM para interação com banco de dados
- **✅ Pydantic** - Validação de dados e configurações
- **📅 python-dateutil** - Cálculos precisos de data/idade
- **🐬 PyMySQL** - Driver Python para MariaDB/MySQL

#### Frontend
- **🌐 HTML5** - Estrutura das páginas
- **🎨 Tailwind CSS** - Framework CSS utilitário
- **⚡ JavaScript ES6+** - Interatividade e AJAX
- **🎯 Lucide Icons** - Ícones SVG modernos
- **📊 Chart.js** - Gráficos interativos
- **📄 jsPDF** - Geração de relatórios PDF
- **🧩 Jinja2** - Engine de templates

#### Banco de Dados
- **🗄️ MariaDB/MySQL** - Banco de dados relacional
- **📊 Tabelas de Referência** - Dados SISVAN/OMS

---

## ⚙️ Configuração e Instalação

### 📋 Pré-requisitos

- **Python 3.8+** instalado
- **MariaDB/MySQL** configurado
- **Git** (para clonagem do repositório)

### 🔧 Passo a Passo

1. **Clonar o Repositório**
   ```bash
   git clone <url-do-repositorio>
   cd projeto_ic_antropometria
   ```

2. **Criar Ambiente Virtual**
   ```bash
   python -m venv ambiente
   ambiente\Scripts\activate  # Windows
   # source ambiente/bin/activate # Linux/macOS
   ```

3. **Instalar Dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Banco de Dados**
   ```sql
   CREATE DATABASE antropometria_db;
   ```

5. **Popular Dados de Referência**
   ```bash
   python scripts/populate_reference_data.py
   ```

6. **Executar Aplicação**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
---

## 🎯 Funcionalidades Detalhadas

### 📊 Dashboard Inteligente

**Visão Geral em Tempo Real:**
- 📈 **Estatísticas Dinâmicas**: Avaliações realizadas, eutróficos, alertas nutricionais
- 🕒 **Atividades Recentes**: Últimas 5 avaliações com dados completos
- 📊 **Gráficos Interativos**: Distribuição do estado nutricional

**Tabela de Atividades Recentes:**
1. **Nome** - Nome completo da pessoa avaliada
2. **Idade** - Idade calculada (ex: "5 anos e 3 meses")
3. **Data de Nascimento** - Formato brasileiro (DD/MM/AAAA)
4. **Data da Avaliação** - Data da avaliação (DD/MM/AAAA)
5. **Peso (kg)** - Peso em quilogramas
6. **Peso/Idade** - Classificação com badge colorido
7. **Altura (cm)** - Altura em centímetros
8. **Altura/Idade** - Classificação com badge colorido
9. **IMC** - Índice de Massa Corporal
10. **IMC/Idade** - Classificação com badge colorido

### 🧑‍⚕️ Avaliação Individual

**Interface Intuitiva:**
- 📝 **Formulário Validado**: Campos obrigatórios e opcionais
- ⚡ **Processamento Rápido**: Resultados em tempo real
- 🎨 **Tabela Padronizada**: Mesma estrutura do dashboard
- 🔄 **Limpeza Automática**: Botão para limpar formulário

**Dados Processados:**
- Cálculo preciso de idade (anos, meses, dias)
- IMC automático com precisão de 2 casas decimais
- Classificações nutricionais com códigos de cores
- Dados formatados para visualização brasileira

### 📁 Avaliação em Lote

**Processamento Eficiente:**
- 📤 **Upload Inteligente**: Suporte a CSV e TSV
- 📋 **Modelo Disponível**: Template para download
- 🏷️ **Identificação Flexível**: Escola/Comunidade e Turma/Grupo
- 📊 **Relatório Completo**: Sucessos, erros e detalhes

**Recursos Avançados:**
- 🔍 **Validação por Linha**: Detecção individual de erros
- 📈 **Resumo Estatístico**: Total processado, sucessos e falhas
- 📄 **Exportação PDF**: Relatório profissional personalizado
- 🚨 **Tratamento de Erros**: Feedback detalhado para correções

### 📋 Relatórios e Exportação

**Geração de PDF:**
- 🎨 **Design Profissional**: Layout limpo e organizado
- 📊 **Dados Completos**: Todas as 10 colunas padronizadas
- 🏷️ **Identificação Clara**: Escola, turma, data de geração
- 🎯 **Cores Inteligentes**: Destaque para classificações nutricionais

---

## 🔧 Uso da Aplicação

### 🌐 Interface Web

**Acesso Principal:**
- **URL**: http://localhost:8000
- **Navegação**: Menu lateral responsivo
- **Seções**: Dashboard, Individual, Lote, Relatórios, Configurações

### 📱 Design Responsivo

**Dispositivos Suportados:**
- 💻 **Desktop**: Experiência completa
- 📱 **Tablet**: Interface adaptada
- 📲 **Mobile**: Menu hambúrguer otimizado

### ⌨️ Atalhos e Produtividade

**Funcionalidades Rápidas:**
- 🔄 **Auto-preenchimento**: Data de avaliação automática
- ⚡ **Validação Instantânea**: Feedback em tempo real
- 📋 **Limpar Formulários**: Botões dedicados
- 🔍 **Busca Inteligente**: Navegação por seções

---

## 🛠️ API RESTful

### 📡 Endpoints Disponíveis

#### 1. Processamento Individual
```http
POST /api/processar/individual
Content-Type: application/json

{
  "nome": "João Silva",
  "data_nascimento": "2019-03-15",
  "data_avaliacao": "2024-06-15",
  "sexo": "M",
  "peso_kg": 18.5,
  "altura_cm": 105.2
}
```

**Resposta:**
```json
{
  "nome": "João Silva",
  "idade": "5 anos e 3 meses",
  "data_nascimento": "2019-03-15",
  "data_avaliacao": "2024-06-15",
  "peso_kg": 18.5,
  "altura_cm": 105.2,
  "imc": 16.73,
  "indicadores": [
    {
      "tipo": "Peso-para-Idade",
      "valor_medido": 18.5,
      "escore_z": -0.5,
      "classificacao": "Peso adequado para idade"
    }
  ]
}
```

#### 2. Processamento em Lote
```http
POST /api/processar/lote
Content-Type: multipart/form-data

file: [arquivo.csv]
reportIdentifier: "EMEI Criança Feliz"
reportSubIdentifier: "Turma 5º ano"
```

### 📚 Documentação Automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json---

## 🧪 Testes e Qualidade

### 🔍 Testes Automatizados

```bash
# Executar todos os testes
pytest tests/

# Executar testes com cobertura
pytest tests/ --cov=app --cov-report=html

# Executar testes específicos
pytest tests/test_anthropometry_service.py
```

**Tipos de Testes:**
- ✅ **Testes Unitários**: Validação de serviços e cálculos
- 🔗 **Testes de Integração**: Endpoints da API
- 🌐 **Testes End-to-End**: Interface completa

### 📊 Métricas de Qualidade

- **Cobertura de Código**: >85%
- **Validação de Dados**: Pydantic
- **Tratamento de Erros**: Robusto
- **Performance**: Otimizada

---

## 🏥 Dados de Referência

### 📊 Tabelas SISVAN/OMS

**Indicadores Suportados:**
- **Peso/Idade (P/I)**: 0-119 meses
- **Altura/Idade (A/I)**: 0-228 meses  
- **IMC/Idade (IMC/I)**: 0-228 meses

**Classificações Disponíveis:**
- 🔴 **Magreza acentuada**: < -3 Z-score
- 🟠 **Magreza**: -3 a -2 Z-score
- 🟢 **Eutrofia**: -2 a +1 Z-score
- 🟡 **Risco de sobrepeso**: +1 a +2 Z-score
- 🟠 **Sobrepeso**: +2 a +3 Z-score
- 🔴 **Obesidade**: > +3 Z-score

### 🔄 Atualização de Dados

```bash
# Popular/atualizar dados de referência
python scripts/populate_reference_data.py

# Verificar integridade dos dados
python scripts/validate_reference_data.py
```

---

## 🚀 Desenvolvimento e Contribuição

### 🔧 Ambiente de Desenvolvimento

```bash
# Modo desenvolvimento com hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Debug mode
uvicorn app.main:app --reload --log-level debug

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 📋 Padrões de Código

- **Python**: PEP 8, Black formatter
- **JavaScript**: ES6+, Prettier
- **CSS**: BEM methodology, Tailwind
- **Git**: Conventional commits

### 🔄 Workflow de Desenvolvimento

1. **Feature Branch**: Criar branch para nova funcionalidade
2. **Desenvolvimento**: Implementar com testes
3. **Code Review**: Revisão de código
4. **Testing**: Executar suite completa de testes
5. **Deploy**: Merge para main branch

---

## 🛡️ Segurança e Performance

### 🔒 Aspectos de Segurança

- **Validação Robusta**: Pydantic schemas
- **Sanitização**: Inputs HTML e CSV
- **Rate Limiting**: Proteção contra abuse
- **CORS**: Configuração adequada

### ⚡ Otimizações de Performance

- **Lazy Loading**: Carregamento sob demanda
- **Database Pooling**: Conexões otimizadas
- **Caching**: Redis para dados frequentes
- **Compression**: Gzip para assets

---

## 📚 Recursos Adicionais

### 🎓 Documentação Científica

- **SISVAN**: Manual de Orientações
- **OMS**: Growth Standards
- **Metodologia**: Cálculo de Z-scores
- **Validação**: Estudos de referência

### 🔗 Links Úteis

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://sqlalchemy.org/
- **Tailwind CSS**: https://tailwindcss.com/
- **Chart.js**: https://chartjs.org/

### 📞 Suporte e Contato

- **Desenvolvedor**: João Paulo Oliveira Braga
- **Instituição**: LABDIS - UNIFESP
- **Email**: [contato@labdis.unifesp.br]
- **Documentação**: [Wiki do projeto]

---

## 📜 Licença

Este projeto é desenvolvido como parte de um Projeto de Iniciação Científica no LABDIS - UNIFESP.

**Copyright © 2025 LABDIS - UNIFESP**  
**Todos os direitos reservados.**

---

## 🎉 Agradecimentos

- **LABDIS - UNIFESP** pelo suporte institucional
- **Orientadores** pela supervisão técnica
- **Comunidade Open Source** pelas ferramentas utilizadas
- **SISVAN/OMS** pelos dados de referência
