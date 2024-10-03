import csv
import time
import requests
import datetime
import pytz
from decimal import Decimal
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
from app.blueprints.models import Video
from app.blueprints.models import Thumb
from app.extensions.database import db

# SQLAlchemy
from sqlalchemy import func

# XML
import xml.etree.ElementTree as ET

def index():
    municipios = db.session.query(Municipio).order_by(Municipio.total_votos.desc()).all()
    return render_template("index.html", municipios=municipios)

def candidatos(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).first_or_404()   
    candidatos = Candidato.query.filter(Candidato.codigo_municipio == codigo_municipio).all()
    return render_template("candidatos.html", candidatos=candidatos, municipio=municipio)

def criar_video(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).first_or_404()
    candidatos = Candidato.query.filter(Candidato.codigo_municipio == codigo_municipio).all()

    # Pega as configurações do template conforme o número de candidatos
    template = pegar_template(len(candidatos))
        
    parameters = {}
    parameters[f"cidade"] = f"{municipio.nome} ({municipio.UF})"        
    
    parameters[f"cidade2"] = f"{municipio.nome} - {municipio.UF}"
    
    for i, candidato in enumerate(candidatos, start=1):
        parameters[f"candidato{i}Nome"] = quebrar_linha(candidato.nome_urna)
        parameters[f"candidato{i}Partido"] = candidato.partido
        parameters[f"candidato{i}Percentual"] = f"{candidato.percentual_votos_apurados} %"
        parameters[f"candidato{i}Votos"] = f"{candidato.votos_apurados} votos"
        parameters[f"candidato{i}Foto"] = f"https://eleicoes.gorobei.net/static/fotos/FSP250001926547_div.jpg"
    
    for i, candidato in enumerate(candidatos, start=1):
        if Decimal(candidato.votos_apurados) >= ((Decimal(municipio.votos_validos) / 2) + 1):
            parameters[f"turnoResultado"] = "Não haverá segundo turno"
            parameters[f"indicadorEleito"] = "100"
            break
        else:
            parameters[f"turnoResultado"] = "Haverá segundo turno"
            parameters[f"indicador2Turno"] = "100"
    
    # Abstenções
    parameters[f"abstencaoPercentual"] = f"{municipio.percentual_abstencao} %"
    
    # Brancos e Nulos Percentual
    percentual_votos_nulos_brancos = municipio.percentual_votos_branco + municipio.percentual_votos_nulo
    parameters[f"brancosNulosPercentual"] = f"{percentual_votos_nulos_brancos} %"
    
    # Brancos e Nulos Total
    votos_nulos_brancos = municipio.votos_branco + municipio.votos_nulo
    parameters[f"brancosNulosTotal"] = f"{votos_nulos_brancos}"
    
    # Votos Válidos
    parameters[f"votosValidos"] = f"Voto válidos {municipio.votos_validos} ({municipio.percentual_votos_validos}%), fonte TSE votos"
    
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
 
    data = {
        "projectId": f"{template['projectId']}",
        "templateId":  f"{template['templateId']}",
        "parameters": parameters,
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')
    
    print("aqui")
    response = requests.post(
        endpoint, 
        headers=headers, 
        json=data, 
        auth=auth
    )
    
    """video = Video(
        municipio_id=municipio.id,
        data_criacao=datetime.datetime.now(),
        titulo=f"Eleições Municípais: {municipio.nome} - {municipio.UF}",
        descricao=f"Confira o resultado da eleição para prefeito de {municipio.nome} - {municipio.UF}",
        plainly_url=None,
        plainly_id=response.json()['id'],
        plainly_state=response.json()['state'],
        plainly_template_name=response.json()['projectName'],
        plainly_template_id=response.json()['projectId'],
        plainly_thumbnail_uri=""
    )
    db.session.add(video)
    db.session.commit() """
    
    
    #return jsonify(data)
    return redirect(url_for('webui.index'))    


def pegar_template(nm_candidatos):
    templates = [
        {
            'projectId': 'bd7ffc02-8f57-4795-be33-ec64b6b2ef09',
            'templateId': 'c0250f96-42e4-4c09-80ab-ce32e75254d9',
            'nm_candidados': 3
        },
        {
            'projectId': 'a66e8c0c-89c8-4440-8c24-cdf60d10f5bc',
            'templateId': '30e42b94-70ee-4e89-be42-5e52289a7103',
            'nm_candidados': 4
        },
        {
            'projectId': 'edf83540-bb85-4b59-8b87-de84dd166275',
            'templateId': '175d6370-8bb6-402d-bb30-b1596cf289a7',
            'nm_candidados': 5
        },
        {
            'projectId': '02fed3ad-64dd-40e1-8e8e-9c95dd82a162',
            'templateId': '03356aa3-4311-4add-a61a-481ac988a3cf',
            'nm_candidados': 6
        },
        {
            'projectId': '3bcdfcf5-d1c4-4a57-bf14-28b87570e2a8',
            'templateId': '0cb1f2ec-bc6f-49a4-adb7-d6454f7ca9ac',
            'nm_candidados': 7
        },
        {
            'projectId': '0009aa7c-d31f-4b07-aaf7-1a3a82372c91',
            'templateId': '352f14a6-6aef-4cbe-aa5d-e57564aa73ea',
            'nm_candidados': 8
        },
        {
            'projectId': 'ddd74c5a-7f96-47e8-a12f-b79f3871f1ec',
            'templateId': 'b397a545-0fe9-4b15-b37a-18df2c538b83',
            'nm_candidados': 9
        },
        {
            'projectId': '79efcf99-b957-4acd-8625-4ec29137bc75',
            'templateId': 'f89e0126-fbda-477e-bbf3-2557cc2c8cea',
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
            
            time.sleep(10)
            """  response = requests.get(
                    f"{endpoint}/{thumb.plainly_id}",
                    headers=headers,
                    auth=auth
                )
            
            thumb.plainly_thumbnail_uri=response.json()['thumbnailUris']
            db.session.commit() """
        
    return redirect(url_for('webui.thumbs_list'))

def thumbs_list():
    thumbs = Thumb.query.all()
    return render_template('thumbs.html', thumbs=thumbs)


def thumbs_update():
    thumbs = Thumb.query.all()
    for thumb in thumbs:
        
        if thumb.plainly_thumbnail_uri is None or thumb.plainly_thumbnail_uri == "":    
            endpoint = "https://api.plainlyvideos.com/api/v2/renders"
            headers = {
                "Content-Type": "application/json"
            }
            auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')

            response = requests.get(
                f"{endpoint}/{thumb.plainly_id}",
                headers=headers,
                auth=auth
            )

            thumb.plainly_thumbnail_uri=response.json()['thumbnailUris']
            db.session.commit()
            time.sleep(5)
            
    return redirect(url_for('webui.thumbs_list'))


def terra_json(nome_normalizado):
    url = "https://p1-cloud.trrsf.com/api/eleicoes2024-api/resultados"
    params = {
        "municipio": nome_normalizado
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)
    return jsonify(response.json())