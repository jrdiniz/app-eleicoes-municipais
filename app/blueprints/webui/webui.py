import csv
import requests
import datetime
from requests.auth import HTTPBasicAuth

from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import render_template
from flask import current_app
from io import StringIO

from app.blueprints.models import Candidato
from app.blueprints.models import Municipio
from app.blueprints.models import Artigo
from app.blueprints.models import Video
from app.extensions.database import db

# SQLAlchemy
from sqlalchemy import func


def index():
    municipios = db.session.query(Municipio.id, Municipio.nm_ue, Municipio.sg_uf, Municipio.nm_eleitores, Municipio.status_apuracao, func.count(Candidato.sq_candidato).label('nm_candidatos')).join(Candidato).group_by(Municipio.id).order_by(Municipio.nm_eleitores.desc()).all()
    return render_template("index.html", municipios=municipios)

def candidatos(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()   
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).all()
    return render_template("candidatos.html", candidatos=candidatos, municipio=municipio)

def criar_artigo(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()
    return render_template("artigo.html", municipio = municipio)


def export_to_csv():
    # Numero maximo de candidatos por municipio
    MAX_CANDIDATOS = 10

    # Create a string buffer to write the CSV data
    si = StringIO()
    csvwriter = csv.writer(si)

    # Create a header row with dynamic columns for each Candidato
    header = [
        'uf','municipio','nulos','brancos','abstencoes','status_apuracao'
    ]
    
    for i in range(1, MAX_CANDIDATOS + 1):
        header.extend([
            f'candidato_{i}_numero', 
            f'candidato_{i}_nome', 
            f'candidato_{i}_ft', 
            f'candidato_{i}_partido', 
            f'candidato_{i}_total_votos', 
            f'candidato_{i}_total_votos_percentual'
        ])
    
    csvwriter.writerow(header)

    # Query all municipios
    municipios = Municipio.query.all()

    for municipio in municipios:
        row = [
            municipio.sg_uf,
            municipio.nm_ue,
            municipio.nm_nulos,
            municipio.nm_brancos,
            municipio.nm_abstencoes,
            municipio.status_apuracao
        ]
        
        candidatos = Candidato.query.filter_by(municipio_id=municipio.id).order_by(Candidato.nr_votos.desc()).limit(MAX_CANDIDATOS).all()


        for candidato in candidatos:
            candidato_percentual = candidato.nr_votos / municipio.nm_eleitores * 100 if municipio.nm_eleitores > 0 else 0   
            ft_candidato_url = f"{request.url_root}static/fotos/{candidato.ft_candidato}"
            row.extend([
                candidato.nr_candidato,
                candidato.nm_urna_candidato,
                f'{ft_candidato_url}',
                candidato.sg_partido,
                candidato.nr_votos,
                f'{candidato_percentual}%'
            ])
        
        csvwriter.writerow(row)

    # Move the cursor of the StringIO buffer to the start
    si.seek(0)

    # Create a Flask Response object to download the CSV
    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='municipio_candidato.csv')
    
    return response

def criar_video(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).all()
    
    parameters = {}
    parameters[f"cidade"] = municipio.nm_ue
    parameters[f"cidade2"] = f"{municipio.nm_ue.title()} - {municipio.sg_uf.upper()}"
    for i, candidato in enumerate(candidatos, start=1):
        parameters[f"candidato{i}Nome"] = candidato.nm_urna_candidato
        parameters[f"candidato{i}Partido"] = candidato.sg_partido
        parameters[f"candidato{i}Foto"] = f"https://eleicoes.gorobei.net/static/fotos/{candidato.ft_candidato}"
    
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "projectId": "dbf95ee8-c2ab-4619-9907-e05f1f539247",
        "templateId": "1b65627d-c5f8-46b6-8912-272f8bbccacc",
        "parameters": parameters
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"],'')
    
    response = requests.post(
        endpoint, 
        headers=headers, 
        json=data, 
        auth=auth
    )
    
    video = Video(
        municipio_id=municipio.id,
        data_criacao=datetime.datetime.now(),
        titulo=f"Eleições Municípais: {municipio.nm_ue.title()} - {municipio.sg_uf.upper()}",
        descricao=f"Confira o resultado da eleição para prefeito de {municipio.nm_ue.title()} - {municipio.sg_uf.upper()}",
        plainly_url=None,
        plainly_id=response.json()['id'],
        plainly_state=response.json()['state'],
        plainly_template_name=response.json()['projectName'],
        plainly_template_id=response.json()['projectId']
    )
    db.session.add(video)
    db.session.commit()
    
    return redirect(url_for('webui.videos'))    

def videos():
    videos = Video.query.all()
    return render_template('videos.html', videos=videos)


def video_atualizar_state():
    videos = Video.query.all()
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')

    for video in videos:
        if video.plainly_state == 'PENDING':
            response = requests.get(
                f"{endpoint}/{video.plainly_id}",
                headers=headers,
                auth=auth
            )
            if response.json()['state'] == 'DONE':
                video.plainly_state = response.json()['state']
                video.plainly_url = response.json()['output']
                db.session.commit()

    return redirect(url_for('webui.videos'))