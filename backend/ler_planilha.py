import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SAMPLE_SPREADSHEET_ID = "1IaAbCsXgjQY4n4C1Oujfxiy1Lg4VcCNe-vVt1kHJL8c" 
NOME_DA_ABA = "Registro de Estágios"

LINHA_INICIAL_DADOS = 9

# MAPIAR a chave do JSON para o ÍNDICE da coluna (A=0, B=1, C=2, etc.)
#    Para aninhar, use um ponto (.), como em "conclusao_do_estagio.motivo"
MAPA_DE_COLUNAS = {
    # Chave no JSON final : Índice da Coluna
    "nome_aluno": 0,
    "obrig": 1,
    "empresa": 2,
    "tce_entregue": 3,

    # Exemplo para o objeto aninhado "conclusao_do_estagio"
    "conclusao_do_estagio.data_realizado": 4,
    "conclusao_do_estagio.motivo": 5,

    "prazo_maximo": 6,
    "orientador_designado_por_articulador_atual": 7,
    "orientador_designado_por_articulador_anterior": 8,
    "fpe.limite": 9,
    "fpe.realizado": 10,
    "inicio_tce_aprovado": 11,
    "termino_previsto": 12,
    
    # Exemplo para outro objeto aninhado
    "relatorios.parcial_1.limite": 13,
    "relatorios.parcial_1.entregue": 14,
    "relatorios.parcial_1.realizado": 15,
    "relatorios.parcial_2.limite": 16,
    "relatorios.parcial_2.entregue": 17,
    "relatorios.parcial_2.realizado": 18,
    "relatorios.parcial_3.limite": 19,
    "relatorios.parcial_3.entregue": 20,
    "relatorios.parcial_3.realizado": 21,
    "relatorios.final.limite": 22,
    "relatorios.final.entregue": 23,
    "relatorios.final.realizado": 24,
    "prorrogacoes_do_estagio.data_1": 25,
    "prorrogacoes_do_estagio.data_2": 26,
    "prorrogacoes_do_estagio.data_3": 27,

    "supervisor_na_empresa": 28
}

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=NOME_DA_ABA).execute()
        values = result.get("values", [])

        if len(values) < LINHA_INICIAL_DADOS:
            print("Não há linhas de dados para processar.")
            return

        data_rows = values[LINHA_INICIAL_DADOS - 1:]

        lista_de_objetos = []
        for i, row in enumerate(data_rows):
            if not any(row):
                continue
            
            obj = {}
            for chave_mapeada, indice_coluna in MAPA_DE_COLUNAS.items():
                valor = row[indice_coluna].strip() if indice_coluna < len(row) and row[indice_coluna] else ""
                
                #LÓGICA DE ANINHAMENTO CORRIGIDA PARA MÚLTIPLOS NÍVEIS
                parts = chave_mapeada.split('.')
                current_level = obj
                for j, part in enumerate(parts):
                    if j == len(parts) - 1: # Se for a última parte, atribui o valor
                        current_level[part] = valor
                    else: # Se não for a última parte, navega ou cria o nível
                        if part not in current_level:
                            current_level[part] = {}
                        current_level = current_level[part]
            
            valor_nome_aluno = obj.get("nome_aluno")
            print(f"DEBUG (Linha {i + LINHA_INICIAL_DADOS}): Verificando o valor para 'nome_aluno': '{valor_nome_aluno}'")

            if obj and valor_nome_aluno:
                lista_de_objetos.append(obj)
                print("--> APROVADA")
            else:
                print("--> REJEITADA (O nome do aluno está vazio)")
            
        json_output = json.dumps(lista_de_objetos, indent=2, ensure_ascii=False)
        print("\n--- DADOS COM ESTRUTURA ANINHADA (JSON) ---")
        print(json_output)

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()