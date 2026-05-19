# 📊 Extração Automatizada de Dados (Asana API)

## 📌 Sobre o Projeto
Este projeto consiste em scripts desenvolvidos em Python (`main.py` e `funcs.py`) para a extração automatizada e estruturação de dados provenientes da plataforma Asana. O objetivo principal é conectar-se a fontes externas, coletar dados não estruturados e transformá-los em um formato tabular para análises posteriores.

## 🔬 Relação com o Processo KDD
No contexto de Descoberta de Conhecimento em Base de Dados (KDD), este projeto demonstra proficiência nas etapas iniciais e cruciais do processo:
* **Seleção de Dados:** Conexão com a origem e requisição de fatias específicas de informação.
* **Pré-processamento:** Tratamento do retorno da API (frequentemente em formatos complexos como JSON), isolando os atributos relevantes.
* **Transformação:** Conversão dos dados brutos em DataFrames (estruturas tabulares) prontos para a fase de mineração.

## 🛠️ Tecnologias Utilizadas
* **Python** * **Bibliotecas:** `pandas` (para estruturação), `requests` (para integração via API).

## 🚀 Como Executar
1. Clone este repositório.
2. Instale as dependências necessárias.
3. Configure as credenciais/tokens de acesso no arquivo correspondente.
4. Execute o `main.py` para iniciar a rotina de extração.
