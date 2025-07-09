# -*- coding: utf-8 -*-
import os.path
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from apscheduler.schedulers.blocking import BlockingScheduler

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SAMPLE_SPREADSHEET_ID = "1IaAbCsXgjQY4n4C1Oujfxiy1Lg4VcCNe-vVt1kHJL8c"

TAB_NAMES = [
    "Registro de Estágios",
    "Visitas do Articulador",
    "Visitas do Orientador",
    "Usuários"
]

START_LINES_MAP = {
    "Registro de Estágios": 9,
    "Visitas do Articulador": 2,
    "Visitas do Orientador": 2,
    "Usuários": 2
}

COLUMNS_MAP_BY_TAB = {
    "Registro de Estágios": {
        "nome_aluno": 0, "obrig": 1, "empresa": 2, "tce_entregue": 3,
        "conclusao_do_estagio.data_realizado": 4, "conclusao_do_estagio.motivo": 5,
        "prazo_maximo": 6,
        "orientador_designado_por_articulador_atual": 7,
        "orientador_designado_por_articulador_anterior": 8,
        "fpe.limite": 9, "fpe.realizado": 10,
        "inicio_tce_aprovado": 11, "termino_previsto": 12,
        "relatorios.parcial_1.limite": 13, "relatorios.parcial_1.entregue": 14, "relatorios.parcial_1.realizado": 15,
        "relatorios.parcial_2.limite": 16, "relatorios.parcial_2.entregue": 17, "relatorios.parcial_2.realizado": 18,
        "relatorios.parcial_3.limite": 19, "relatorios.parcial_3.entregue": 20, "relatorios.parcial_3.realizado": 21,
        "relatorios.final.limite": 22, "relatorios.final.entregue": 23, "relatorios.final.realizado": 24,
        "prorrogacoes_do_estagio.data_1": 25, "prorrogacoes_do_estagio.data_2": 26, "prorrogacoes_do_estagio.data_3": 27,
        "supervisor_na_empresa": 28
    },
    "Visitas do Articulador": {
        "data_visita": 0, "periodo_visita": 1, "tipo_visita": 2, "efetivada": 3, "empresa": 4,
        "tipificacao_empresa": 5, "supervisor_na_empresa": 6, "cargo": 7,
        "estagiarios_ativos.obrigatorios": 8, "estagiarios_ativos.nao_obrigatorios": 9,
        "resumo_instalacoes": 10, "atividades_principais": 11, "tecnologias_principais": 12,
        "perfil_desejado_estagiarios": 13, "consideracoes_encaminhamentos": 14
    },
    "Visitas do Orientador": {
        "orientador": 0, "data_visita": 1, "periodo_visita": 2, "tipo_visita": 3, "efetivada": 4,
        "empresa": 5, "tipificacao_empresa": 6, "supervisor_na_empresa": 7, "cargo": 8,
        "nome_estagiario": 9, "obrigatorio": 10, "tempo_transcorrido_estagio": 11,
        "atividade_principais_atuais": 12, "progresso_atividades_anteriores": 13,
        "comentario_supervisor": 14, "comentario_estagiario": 15, "consideracoes_encaminhamentos": 16
    },
    "Usuários": {
        "nome": 0, "tipo": 1, "login": 2, "senha": 3,
    },
}

def get_creds()-> Credentials:
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
    return creds

def create_json_file(nome_arquivo: str, dados: str):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(dados)

def spreadsheet_is_empty(values: list, linha_inicial: int)-> bool:
    if len(values) < linha_inicial:
        return True
    else:
        return False

def get_data_from_tab(tab_name: str, service)-> list:
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"'{tab_name}'").execute()
    values = result.get("values", [])

    linha_inicial_dados = START_LINES_MAP[tab_name]

    if spreadsheet_is_empty(values, linha_inicial_dados):
        return []

    data_rows = values[linha_inicial_dados - 1:]

    object_list = []
    for i, row in enumerate(data_rows):
        if not any(row):
            continue

        obj = {}
        for maped_key, column_index in COLUMNS_MAP_BY_TAB[tab_name].items():
            valor = row[column_index].strip() if column_index < len(row) else ""

            parts = maped_key.split('.')
            current_level = obj
            for j, part in enumerate(parts):
                if j == len(parts) - 1:
                    current_level[part] = valor
                else:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]

        if tab_name == "Registro de Estágios" and obj.get("nome_aluno"):
            object_list.append(obj)
        elif tab_name == "Visitas do Articulador" and obj.get("empresa"):
            object_list.append(obj)
        elif tab_name == "Visitas do Orientador" and obj.get("nome_estagiario"):
            object_list.append(obj)
        elif tab_name == "Usuários" and obj.get("nome"):
            object_list.append(obj)

    return object_list

def get_data_from_spreadsheet()-> dict:
    full_data = {}
    creds = get_creds()
    try:
        service = build("sheets", "v4", credentials=creds)
        for tab in TAB_NAMES:
            full_data[tab] = get_data_from_tab(tab, service)
        return full_data
    except HttpError as err:
        return {}

def run_spreadsheet_data_job():
    all_spreadsheet_data = get_data_from_spreadsheet()

    if not all_spreadsheet_data:
        return

    for tab_name, data_list in all_spreadsheet_data.items():
        file_name = tab_name.lower().replace(" ", "_").replace("ã", "a").replace("á","a").replace("ç", "c").replace("í", "i") + ".json"
        json_output = json.dumps(data_list, indent=2, ensure_ascii=False)
        create_json_file(file_name, json_output)


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(run_spreadsheet_data_job, 'interval', minutes=1, start_date=datetime.datetime.now())

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass