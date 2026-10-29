# 🛡️ Portal de Vigilância Epidemiológica (e-SUS APS)

Uma plataforma web analítica desenvolvida para monitoramento epidemiológico, auditoria e fiscalização da Atenção Primária à Saúde (APS). O sistema atua conectando-se ao banco de dados transacional do **e-SUS APS**, isolando dados complexos através de **Visões Materializadas (Materialized Views)** e oferecendo painéis de decisão em tempo real.

Este projeto visa solucionar o **"Hiato Informacional"** — a latência e subnotificação entre o registro clínico na ponta (Posto de Saúde) e a notificação oficial para os órgãos do governo (SINAN).

---

## ✨ Principais Funcionalidades

* **Arquitetura OLAP Otimizada:** Processa bancos de dados governamentais massivos (ex: 18 GB) transferindo o custo computacional para o *background* usando *Materialized Views* no PostgreSQL.
* **Painéis Interativos (Data Discovery):** Filtros geoespaciais (Bairros e Unidades), série histórica, mapeamento demográfico e perfis sintomatológicos (CIAP-2).
* **Auditoria de Exames:** Monitoramento estruturado de solicitações e laudos laboratoriais, incluindo cálculo de Tempo de Resposta (SLA) do laboratório.
* **Sistema de Alertas Inteligente:** Disparo automático de e-mails para gestores caso o sistema detecte aumento no número de casos confirmados de doenças monitoradas (ex: Febre Maculosa, Dengue, COVID-19).
* **Anonimização de Dados (LGPD):** Prontuários detalhados exibidos em modais (pop-ups) com anonimização automática de CPFs.

---

## 🏗️ Estrutura do Projeto 

O projeto segue o princípio de **Separação de Responsabilidades (Separation of Concerns)**, dividido em 6 arquivos principais:

1. `main.py`: Arquivo central que orquestra a aplicação web (executado pelo Streamlit).
2. `config.py`: Dicionários e regras de negócio (Mapeamento dinâmico de CIDs e CIAPs).
3. `database.py`: Infraestrutura de banco, conexões (SQLAlchemy) e DDL (criação das Materialized Views).
4. `queries.py`: Lógicas de leitura (SELECTs) e filtros retornando DataFrames do Pandas.
5. `alerts.py`: Lógica isolada de disparo de e-mails (SMTP) e salvamento de configurações JSON.
6. `ui.py`: Componentes visuais isolados (estilos CSS customizados e Modais).

---

## 🚀 Como Instalar e Rodar o Projeto

### 1. Pré-requisitos
* **Python 3.8+** instalado.
* **PostgreSQL 12+** instalado e rodando.
* Arquivo de backup do banco de dados do **e-SUS APS** restaurado localmente ou em servidor acessível.

### 2. Instalação das Dependências
Clone este repositório, abra o terminal na pasta do projeto e instale as bibliotecas necessárias:

```bash
pip install streamlit pandas plotly sqlalchemy psycopg2
```
*(Nota: O `psycopg2` é o driver necessário para que o SQLAlchemy converse com o PostgreSQL).*

### 3. Configurando a Conexão com o Banco de Dados
Antes de rodar, você precisa apontar o sistema para o seu banco de dados local.
Abra o arquivo **`database.py`** e localize a linha de conexão (`create_engine`). Altere as credenciais para as do seu servidor:

```python
# Formato: postgresql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
engine = create_engine("postgresql://postgres:sua_senha_aqui@localhost:5432/seu_banco_esus")
```
*Faça o mesmo no arquivo **`main.py`** se a string de conexão estiver declarada no cabeçalho.*

### 4. Executando a Aplicação
Com o terminal aberto na pasta onde estão os 6 arquivos, execute o comando:

```bash
streamlit run main.py
```
O painel será aberto automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

---

## 📖 Guia de Uso

### Passo 1: A Primeira Sincronização
Ao abrir o painel pela primeira vez, os gráficos aparecerão vazios. Você precisa criar a inteligência analítica no banco de dados:
1. Abra a barra lateral esquerda.
2. Clique no botão laranja **"🔄 Sincronizar Todas as Bases"**.
3. O servidor PostgreSQL processará os gigabytes de dados transacionais e criará os "resumos otimizados" (MatViews) no disco. Isso pode levar alguns minutos (processamento em lote).

### Passo 2: Navegando pelos Dados
* **Seletor Superior:** Escolha o agravo (Dengue, COVID, Sífilis, etc.) para alterar o contexto de todo o painel.
* **Tabelas Interativas:** Na aba "Dados Gerais", clique sobre qualquer linha da tabela de *Ocorrências Recentes* para abrir um modal flutuante com os dados detalhados do paciente e alertas de febre/internação.

### Passo 3: Configurando Alertas por E-mail
Para que o sistema avise os gestores sobre surtos automaticamente após uma sincronização:
1. Na barra lateral, expanda **"⚙️ Configurar alertas"**.
2. Selecione quais doenças devem ser monitoradas.
3. Insira o e-mail do remetente e os destinatários.
4. **Senha de App (Gmail):** O Google não permite o uso da sua senha normal. Você deve gerar uma **Senha de Aplicativo**:
   * Acesse: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   * Gere uma senha de 16 letras, copie e cole no painel.
5. Clique em **"💾 Salvar Configurações"**.

---

## 👨‍💻 Autor
**Felipe Parreiras Dias**
* Engenharia de Computação - CEFET-MG (Campus Divinópolis)
* Projeto desenvolvido como Trabalho de Conclusão de Curso (PFC).
