#%%
import sys
import asana
import pandas as pd
from datetime import datetime, timezone
from asana.rest import ApiException

# --- Imports do seu ambiente (Proxy, etc.) ---
try:
    # Importa as funções do seu novo arquivo funcs.py
    from extracao_Asana.src.funcs import proxy_corporativo, obter_usuario_logado
    
    print("Ativando proxy...")
    proxy_corporativo() # Ativando seu proxy
    
    matricula = obter_usuario_logado()
    print(f"Script executado pelo usuário: {matricula}")
    
except ImportError:
    print("Aviso: Não foi possível importar 'funcs.py'.")
    print("Continuando sem proxy. Isso pode falhar na sua rede corporativa.")
except Exception as e:
    print(f"Erro ao inicializar funcs.py: {e}")
# --- Fim dos imports locais ---


# --- 1. CONFIGURAÇÃO DA API ---
configuration = asana.Configuration()

# !! PREENCHA SEU TOKEN AQUI !!
configuration.access_token = '<SEU_TOKEN_DE_ACESSO_ASANA_AQUI>' 

api_client = asana.ApiClient(configuration)
tasks_api_instance = asana.TasksApi(api_client)

# --- 2. DEFINIÇÃO DOS PROJETOS E FILTROS ---

# !! PREENCHA O GID DO PROJETO AQUI !!
project_gids = ['<GID_DO_PROJETO_ASANA>'] # GID do projeto alvo

# Lista para armazenar dados das tasks e subtasks
tasks_data = []

# Campos desejados para coleta
fields = [
    "gid", "created_at", "completed_at", "modified_at", "name", "memberships.section.name", 
    "assignee.name", "assignee.email", "start_on", "due_on", "tags.name", "notes", "projects.name", 
    "parent", "dependencies", "dependents", "custom_fields"
]

# --- REATIVANDO O FILTRO DE DATA CONFORME SOLICITADO ---
maior_data = pd.to_datetime("2025-09-01") 

# --- 3. FUNÇÃO PARA BUSCAR SUBTASKS (CORRIGIDA) ---
def fetch_subtasks(task_gid, parent_name):
    """Busca e formata as subtasks de uma tarefa pai."""
    try:
        # A API (plural) retorna um generator de DICIONÁRIOS (resumos)
        subtasks_generator = tasks_api_instance.get_subtasks_for_task(task_gid, {})
        subtasks_data = []
        
        for subtask_summary in subtasks_generator:
            
            subtask_gid = subtask_summary.get('gid', '')
            if not subtask_gid:
                continue

            opts = {'opt_fields': ','.join(fields)}
            
            # --- CORREÇÃO DO ERRO AQUI ---
            # A API (singular) também retorna um DICIONÁRIO, não um objeto.
            # Removemos o .data.to_dict()
            subtask_details = tasks_api_instance.get_task(subtask_gid, opts)

            modified_at_str = subtask_details.get('modified_at', '')
            if not modified_at_str:
                continue 

            # --- REATIVANDO O FILTRO DE DATA ---
            modified_at = pd.to_datetime(modified_at_str).tz_localize(None)
            if modified_at < maior_data:
                continue # Pula se for anterior ao filtro

            subtask_info = {
                'Task ID': subtask_details.get('gid', ''),
                'Created At': subtask_details.get('created_at', ''),
                'Completed At': subtask_details.get('completed_at', ''),
                'Last Modified': subtask_details.get('modified_at', ''),
                'Name': subtask_details.get('name', ''),
                'Section/Column': 'Subtask', # Subtasks não têm seções
                'Assignee': subtask_details.get('assignee', {}).get('name', '') if subtask_details.get('assignee') else '',
                'Assignee Email': subtask_details.get('assignee', {}).get('email', '') if subtask_details.get('assignee') else '',
                'Start Date': subtask_details.get('start_on', ''),
                'Due Date': subtask_details.get('due_on', ''),
                'Tags': ', '.join(tag.get('name', '') for tag in subtask_details.get('tags', []) if tag),
                'Notes': subtask_details.get('notes', ''),
                'Projects': ', '.join(proj.get('name', '') for proj in subtask_details.get('projects', []) if proj),
                'Parent Task': parent_name,
                'Blocked By (Dependencies)': ', '.join(dep.get('name', '') for dep in subtask_details.get('dependencies', []) if dep),
                'Blocking (Dependencies)': ', '.join(dep.get('name', '') for dep in subtask_details.get('dependents', []) if dep),
                'Campo_Custom_1': '',
                'Campo_Custom_2': '',
                'Campo_Custom_3': '',
                'Campo_Custom_4': '',
                'Campo_Custom_5': ''
            }
            
            if 'custom_fields' in subtask_details:
                for field in subtask_details['custom_fields']:
                    field_name = field.get('name', '')
                    field_value = field.get('display_value', '')

                    if field_name in subtask_info:
                        subtask_info[field_name] = field_value

            subtasks_data.append(subtask_info)

        return subtasks_data

    except ApiException as e:
        print(f"Exception fetching subtasks for task {task_gid}: {e}")
        return []

# --- 4. LOOP PRINCIPAL PARA BUSCAR TAREFAS (CORRIGIDO) ---
for project_gid in project_gids:
    print(f"Buscando tarefas para o projeto GID: {project_gid}...")
    
    try:
        opts = {
            'limit': 100,
            'opt_fields': ','.join(fields)
        }

        # A API (plural) retorna um generator de DICIONÁRIOS
        tasks_generator = tasks_api_instance.get_tasks_for_project(project_gid, opts)

        for task in tasks_generator:
            
            if not task:
                continue
            
            modified_at_str = task.get('modified_at', '')
            if not modified_at_str:
                continue 

            # --- REATIVANDO O FILTRO DE DATA ---
            modified_at = pd.to_datetime(modified_at_str).tz_localize(None)
            if modified_at < maior_data:
                continue # Pula se for anterior ao filtro

            task_info = {
                'Task ID': task.get('gid', ''),
                'Created At': task.get('created_at', ''),
                'Completed At': task.get('completed_at', ''),
                'Last Modified': task.get('modified_at', ''),
                'Name': task.get('name', ''),
                'Section/Column': (task.get('memberships', [{}])[0].get('section', {}).get('name', '') 
                                        if task.get('memberships') else ''),
                'Assignee': task.get('assignee', {}).get('name', '') if task.get('assignee') else '',
                'Assignee Email': task.get('assignee', {}).get('email', '') if task.get('assignee') else '',
                'Start Date': task.get('start_on', ''),
                'Due Date': task.get('due_on', ''),
                'Tags': ', '.join(tag.get('name', '') for tag in task.get('tags', []) if tag),
                'Notes': task.get('notes', ''),
                'Projects': ', '.join(proj.get('name', '') for proj in task.get('projects', []) if proj),
                'Parent Task': '', # É uma tarefa principal, não tem pai
                'Blocked By (Dependencies)': ', '.join(dep.get('name', '') for dep in task.get('dependencies', []) if dep),
                'Blocking (Dependencies)': ', '.join(dep.get('name', '') for dep in task.get('dependents', []) if dep),
                'Campo_Custom_1': '',
                'Campo_Custom_2': '',
                'Campo_Custom_3': '',
                'Campo_Custom_4': '',
                'Campo_Custom_5': ''
            }

            if 'custom_fields' in task:
                for field in task['custom_fields']:
                    field_name = field.get('name', '')
                    field_value = field.get('display_value', '')

                    if field_name in task_info:
                        task_info[field_name] = field_value

            tasks_data.append(task_info)
            
            # Buscar subtasks desta tarefa
            task_gid = task.get('gid')
            if task_gid:
                print(f"Buscando subtasks para: {task.get('name', '')[:50]}...") # Print para debug
                subtasks = fetch_subtasks(task_gid, task.get('name', '')) # Passa o NOME da tarefa pai
                tasks_data.extend(subtasks)

    except ApiException as e:
        print("Exception when calling TasksApi->get_tasks_for_project: %s\n" % e)
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

# --- 5. CRIAR DATAFRAME E SALVAR EM EXCEL ---
print("\nBusca concluída. Gerando DataFrame...")

if not tasks_data:
    print("AVISO: Nenhuma tarefa foi encontrada (após o filtro de data). O arquivo Excel ficará vazio.")

df = pd.DataFrame(tasks_data)
df['DT_INSERCAO_BD'] = pd.to_datetime(datetime.today().date())

# Renomear colunas
df = df.rename(columns={
    'Task ID': 'ID_TAREFA',
    'Created At': 'DT_CRIACAO',
    'Completed At': 'DT_TAREFA_COMPLETA',
    'Last Modified': 'DT_ULTIMA_MODIFICACAO',
    'Name': 'DS_NOME',
    'Section/Column': 'DS_SECAO',
    'Assignee': 'DS_RESPONSAVEL',
    'Assignee Email': 'DS_EMAIL_RESPONSAVEL',
    'Start Date': 'DT_INICIO',
    'Due Date': 'DT_VENCIMENTO',
    'Tags': 'DS_TAGS',
    'Notes': 'DS_NOTAS',
    'Projects': 'DS_PROJETO',
    'Parent Task': 'ID_TAREFA_PAI',
    'Blocked By (Dependencies)': 'DS_BLOCKED_BY_DEPENDENCIES',
    'Blocking (Dependencies)': 'DS_BLOCKING_DEPENDENCIES',
    'DT_INSERCAO_BD': 'DT_INSERCAO_BD'
})

# *** SALVAR EM ARQUIVO EXCEL (.xlsx) ***
nome_arquivo_excel = 'extracao_asana.xlsx'
try:
    df.to_excel(nome_arquivo_excel, index=False, engine='openpyxl')
    print(f"\nSucesso! Os dados foram salvos em '{nome_arquivo_excel}'")
    print(df.head())
except Exception as e:
    print(f"Erro ao salvar arquivo Excel: {e}")

print("\nProcesso finalizado.")