import os
import requests
import time
import datetime

from flask import current_app

# Database
from app.blueprints.models import db
from app.blueprints.models import Video
from app.blueprints.models import Candidato
from app.blueprints.models import Municipio

from requests.auth import HTTPBasicAuth

# Celery
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult

logger = get_task_logger(__name__)

@shared_task(ignore_result=False)
def task_pegar_atualizacao():
    municipios = Municipio.query.all()
    for municipio in municipios:
        task_atualizar_apuracao.delay(municipio.codigo_municipio)
        time.sleep(3)

@shared_task(ignore_result=False)
def task_atualizar_apuracao(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).one_or_none()
    if municipio:
        url = "https://p1-cloud.trrsf.com/api/eleicoes2024-api/resultados"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "municipio": municipio.nome_normalizado
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            apuracao = response.json()['0']
            try:
                municipio.ht = apuracao['ht']
                municipio.dt = datetime.datetime.strptime(apuracao['dt'], '%d/%m/%Y').date()
            except Exception as e:
                municipio.dt = datetime.datetime.now().date()
                municipio.ht = datetime.datetime.now().time()   
                print(f"Sem informação de atualização, setando data e hora atual: {e}")

            municipio.matematicamente_definido = apuracao['matematicamente_definido']
            municipio.votos_validos = apuracao['votos_validos']
            municipio.percentual_votos_validos = apuracao['percentual_votos_validos']
            municipio.votos_branco = apuracao['votos_branco']
            municipio.percentual_votos_branco = apuracao['percentual_votos_branco']
            municipio.votos_nulo = apuracao['votos_nulo']
            municipio.percentual_votos_nulo = apuracao['percentual_votos_nulo']
            municipio.totalizacao_final = apuracao['totalizacao_final']
            municipio.abstencao = apuracao['abstencao']
            municipio.percentual_abstencao = apuracao['percentual_abstencao']
            municipio.percentual_secoes_totalizadas = apuracao['percentual_secoes_totalizadas']
            
            for item in apuracao['candidatos']:
                candidato = Candidato.query.filter_by(sqcand=item['sqcand']).one_or_none()
                if candidato:
                    candidato.nro = item['nro']
                    candidato.seq = item['seq']
                    candidato.situacao = item['situacao']
                    candidato.destinacao_voto = item['destinacao_voto']
                    candidato.votos_apurados = item['votos_apurados']
                    candidato.percentual_votos_apurados = item['percentual_votos_apurados']

            db.session.commit()
            return f"Atualizado em {datetime.datetime.now()} - {municipio.nome}"
            
@shared_task(ignore_result=False)
def task_atualizar_video_state():
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')
    videos = Video.query.filter(
        (Video.plainly_state != 'DONE') & 
        (Video.plainly_state != 'INVALID') &
        (Video.plainly_state != 'FAILED')).all()
    
    for video in videos:
        response = requests.get(
            f"{endpoint}/{video.plainly_id}",
            headers=headers,
            auth=auth
        )
        if response.status_code == 200:    
            video.plainly_state = response.json()['state']
            if video.plainly_state == 'DONE':
                video.plainly_url = response.json()['output']
                with open(f"{current_app.config['BASE_DIR']}/app/static/videos/{video.video_id}.mp4", "wb") as f:
                    f.write(response.content)
                    video.video_uri = f"{video.video_id}.mp4"
                    db.session.commit()
                    f.close()
            db.session.commit()
            #return f"Status do vídeo {video.titulo}, planily_id {video.plainly_id} alterado para {video.plainly_state}"
        time.sleep(3) 
    return f"Status dos vídeos atualizados em {datetime.datetime.now()}"