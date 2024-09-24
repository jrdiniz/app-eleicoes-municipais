import csv
import time
import requests
import datetime
import pytz
from requests.auth import HTTPBasicAuth

from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import render_template
from flask import current_app
from flask import jsonify
from io import StringIO

from app.blueprints.models import Candidato
from app.blueprints.models import Municipio
from app.blueprints.models import Artigo
from app.blueprints.models import Video
from app.blueprints.models import Thumb
from app.extensions.database import db

# SQLAlchemy
from sqlalchemy import func

# XML
import xml.etree.ElementTree as ET

def index():
    municipios = db.session.query(Municipio.id, Municipio.nm_ue, Municipio.sg_uf, Municipio.nm_eleitores, Municipio.status_apuracao, func.count(Candidato.sq_candidato).label('nm_candidatos')).join(Candidato).group_by(Municipio.id).order_by(Municipio.nm_eleitores.desc()).all()
    return render_template("index.html", municipios=municipios)

def candidatos(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()   
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).all()
    return render_template("candidatos.html", candidatos=candidatos, municipio=municipio)

def criar_artigo(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).order_by(Candidato.nr_votos.desc()).all()
    for i, candidato in enumerate(candidatos, start=1):
        if (candidato.nr_votos / municipio.nm_eleitores * 100) >= 50.01:
            segundo_turno = False
            break
        else:
            segundo_turno = True
    return render_template("artigo.html", municipio = municipio, candidatos = candidatos,segundo_turno = segundo_turno)


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
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).order_by(Candidato.nr_votos.desc()).all()

    # Pega as configurações do template conforme o número de candidatos
    template = pegar_template(len(candidatos))
        
    parameters = {}
    parameters[f"cidade"] = municipio.nm_ue
    
    # Determina se haverá segundo turno
    if municipio.segundo_turno:
        parameters[f"turnoResultado"] = "Haverá segundo turno"
        parameters[f"disputa2TurnoC1"] = str(100)
        parameters[f"disputa2TurnoC2"] = str(100)
    else:
        parameters[f"turnoResultado"] = "Não haverá segundo turno"
        parameters[f"semSegundoTurno"] = str(100)
        
    # Status da Apuração
    parameters[f"urnasApuradas"] = "Eleição matematicamente definida"
    
    parameters[f"cidade2"] = f"{municipio.nm_ue} - {municipio.sg_uf.upper()}"
    if len(candidatos) >= 5:
        parameters[f"cidade3"] = f"{municipio.nm_ue} - {municipio.sg_uf.upper()}"
    
    for i, candidato in enumerate(candidatos, start=1):
        parameters[f"candidato{i}Nome"] = quebrar_linha(candidato.nm_urna_candidato)
        parameters[f"candidato{i}Partido"] = candidato.sg_partido
        parameters[f"candidato{i}Percentual"] = f"{candidato.nr_votos / municipio.nm_eleitores * 100:.2f} %"
        parameters[f"candidato{i}Votos"] = f"{candidato.nr_votos} votos"
        parameters[f"candidato{i}Foto"] = f"https://eleicoes.gorobei.net/static/fotos/{candidato.ft_candidato}"
    
    for i, candidato in enumerate(candidatos, start=1):
        if (candidato.nr_votos / municipio.nm_eleitores * 100) >= 50.01:
            parameters[f"turnoResultado"] = "Não haverá segundo turno"
            parameters[f"indicadorEleito"] = "100"
            break
        else:
            parameters[f"turnoResultado"] = "Haverá segundo turno"
            parameters[f"indicador2Turno"] = "100"
    
    # Abstenções
    parameters[f"abstencaoPercentual"] = f"{municipio.nm_abstencoes / municipio.nm_eleitores * 100:.2f} %"
    parameters[f"abstencaoTotal"] = f"{municipio.nm_abstencoes}"
    
    # Brancos e Nulos
    parameters[f"brancosNulosPercentual"] = f"{(municipio.nm_brancos_nulos) / municipio.nm_eleitores * 100:.2f} %"
    parameters[f"brancosNulosTotal"] = f"{municipio.nm_brancos_nulos} votos"

    
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "projectId": f"{template['projectId']}",
        "templateId":  f"{template['templateId']}",
        "parameters": parameters,
        "options": {
            "integrations": {
                "passthrough": f"Resultado Eleições Municípais em {municipio.nm_ue.title()} - {municipio.sg_uf.upper()}",
            }
        }
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')
    
    
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
        plainly_template_id=response.json()['projectId'],
        plainly_thumbnail_uri=""
    )
    db.session.add(video)
    db.session.commit()
    
    
    #return jsonify(data)
    return redirect(url_for('webui.videos'))    


def pegar_template(nm_candidatos):
    templates = [
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 3
        },
        {
            'projectId': 'd889a065-eba5-4bb9-901e-d0e31727284a',
            'templateId': "e0091f83-ef0e-40a5-a8a2-2af459c74e47",
            'nm_candidados': 4
        },
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 5
        },
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 6
        },
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 7
        },
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 8
        },
        {
            'projectId': '',
            'templateId': "1b65627d-c5f8-46b6-8912-272f8bbccacc",
            'nm_candidados': 9
        },
        {
            'projectId': '90e73e3d-2c18-47d2-a49d-bf9cb6513518',
            'templateId': "7df8aa80-0831-4633-8a08-ed0e5c89b8dc",
            'nm_candidados': 10
        }
    ]
    for template in templates:
        if template['nm_candidados'] == int(nm_candidatos):
            return template


def quebrar_linha(nome_candidato):
    if ' ' in nome_candidato:
        primeiro_escapo = nome_candidato.split(' ', 1)
        return primeiro_escapo[0] + '\n' + primeiro_escapo[1]
    return nome_candidato
    
def videos():
    videos = Video.query.order_by(Video.data_criacao.desc()).all()
    return render_template('videos.html', videos=videos)


def video_lista():
    videos = Video.query.order_by(Video.data_criacao.desc()).all()
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')

    for video in videos:
        if video.plainly_state != 'PENDING' or video.plainly_state != 'INVALID':
            response = requests.get(
                f"{endpoint}/{video.plainly_id}",
                headers=headers,
                auth=auth
            )
            video.plainly_state = response.json()['state']
            video.plainly_url = response.json()['output']
            video.plainly_thumbnail_uri=response.json()['thumbnailUris']
            db.session.commit()
            
    return render_template('partials/_video_lista.html', videos = videos)


def delete_video(video_id):
    video = Video.query.get(video_id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('webui.videos'))

def criar_feed():
    videos = Video.query.order_by(Video.data_criacao.desc()).all()
    rss_datetime = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))

    rss = ET.Element("rss")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    rss.set("version", "2.0")

    channel = ET.SubElement(rss, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Feed Resultado Eleições Municipais"

    description = ET.SubElement(channel, "description")
    description.text = "Feed importação dos vídeos gerados de forma automática"

    link = ET.SubElement(channel, "link")
    link.text = f"{request.host_url}rss"

    lastBuildDate = ET.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = rss_datetime.strftime("%a, %d %b %Y %H:%M:%S %z")

    for video in videos:
        if video.plainly_state == 'DONE':
            tz = pytz.timezone("America/Sao_Paulo")
            # Item
            item = ET.SubElement(channel, "item")
            item_title = ET.SubElement(item, "title")
            item_title.text = video.titulo

            item_link = ET.SubElement(item, "link")
            item_link.text = f"{video.plainly_url}"

            item_guid = ET.SubElement(item, "guid")
            item_guid.set("isPermaLink", "false")
            item_guid.text = video.plainly_id

            item_description = ET.SubElement(item, "description")
            item_description.text = video.descricao

            item_category = ET.SubElement(item, "category")
            item_category.text = f"eleições"

            item_pubdate = ET.SubElement(item, "pubDate")
            item_pubdate.text = (
                video.data_criacao.strftime("%a, %d %b %Y %H:%M:%S") + " -0300"
            )

            item_media_content = ET.SubElement(item, "media:content")
            item_media_content.set(
                "url", f"{video.plainly_url}"
            )
            item_media_content.set("type", "video/mp4")
            item_media_content.set("duration", "57")

            item_media_thumbnail = ET.SubElement(item_media_content, "media:thumbnail")
            item_media_thumbnail.set("url", video.plainly_thumbnail_uri)

    return Response(
        ET.tostring(rss, encoding="utf-8", xml_declaration=True),
        mimetype="application/xml",
    )

def thumbs():
    thumbs = Thumb.query.all()
    
    result = []
    for thumb in thumbs:
        if thumb.plainly_thumbnail_uri:
            item = {}
            municipio = Municipio.query.filter_by(id=thumb.municipio_id).one_or_none()
            item['municipio'] = municipio.nm_ue.lower()
            item['plainly_thumbnail_uri'] = thumb.plainly_thumbnail_uri
            result.append(item)
    return jsonify(result)

def gerar_todos_os_thumbs():
    municipios = Municipio.query.all()
    
    for municipio in municipios:
        thumb = Thumb.query.filter_by(municipio_id=municipio.id).one_or_none()
        if thumb is None:
        
            parameters = {}
            parameters["cidade"] = municipio.nm_ue
            
            endpoint = "https://api.plainlyvideos.com/api/v2/renders"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "projectId": f"b0617d4d-b3cf-4da3-86c3-b68a2e69441a",
                "templateId":  f"c9552045-f7d4-46e1-b688-be89a1fb4acd",
                "parameters": parameters,
            }
            auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')
            
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=data, 
                auth=auth
            )
            thumb = Thumb(
                municipio_id=municipio.id,
                plainly_id=response.json()['id'],
                plainly_state=response.json()['state'],
                plainly_thumbnail_uri=""
            )
            db.session.add(thumb)
            db.session.commit()
            
            time.sleep(60)
            response = requests.get(
                    f"{endpoint}/{thumb.plainly_id}",
                    headers=headers,
                    auth=auth
                )
            
            thumb.plainly_thumbnail_uri=response.json()['thumbnailUris']
            db.session.commit()
        
    return render_template('thumbs.html', municipios=municipios)

