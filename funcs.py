import os
import getpass
from snowflake.snowpark.session import Session
import pyodbc
import time


def obter_usuario_logado():
    """Obtém o nome de usuário da conta atualmente logada no Windows."""
    try:
        nome_usuario = os.environ.get('USERNAME') or getpass.getuser()
        return nome_usuario if nome_usuario else "Usuário não identificado"
    except Exception as e:
        print(f"Erro ao obter nome de usuário: {e}")
        return "Usuário não identificado"

def snowflake_conexao_padrao(matricula):
    """Conecta ao Snowflake usando autenticação externa."""
    connection_parameters = {
        'account': '<SNOWFLAKE_ACCOUNT>',
        'user': f'{matricula}@<DOMINIO_EMPRESA>.com.br',
        'authenticator': 'externalbrowser',
        'role': '<ROLE_NAME>',
        'warehouse': '<WAREHOUSE_NAME>',
        'database': '<DATABASE_NAME>',
        'schema': '<SCHEMA_NAME>',
        'client_session_keep_alive': True
    }
    return Session.builder.configs(connection_parameters).create()

def conectar_sql_server():
    """Conecta ao SQL Server."""
    return pyodbc.connect(
        "Driver={SQL Server Native Client 11.0};"
        "Server=<SERVER_NAME>;"
        "Database=<DATABASE_NAME>;"
        "Trusted_Connection=yes"
    )

def proxy_corporativo():
    """
        Realiza as configurações do Proxy Corporativo.
    """
    # Declara a variável que contém as informações do proxy
    proxy_url = "http://<URL_PROXY_CORPORATIVO>:<PORTA>"

    # Configuração global do proxy para todas as solicitações HTTP
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url