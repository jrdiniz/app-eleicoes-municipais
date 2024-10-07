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
from flask import flash
from flask import send_file
from flask import abort
from io import StringIO

from app.blueprints.models import Candidato
from app.blueprints.models import Municipio
from app.blueprints.models import Video
from app.blueprints.models import User
from app.extensions.database import db

# Authentication
from app.extensions.authentication import login_manager
from app.extensions.authentication import login_user
from app.extensions.authentication import login_required
from app.extensions.authentication import logout_user

# Encrypt
from app.extensions.encrypt import bcrypt

# SQLAlchemy
from sqlalchemy import func

# XML
import xml.etree.ElementTree as ET
import os
import os


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@login_required
def index():
    municipios = db.session.query(Municipio).order_by(Municipio.totalizacao_final.desc()).all()
    return render_template("index.html", municipios=municipios)

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('webui.index'))
        else:
            flash("Usuário e/ou Senha Inválidos.", "alert-danger")
    return render_template("login.html")

def logout():
    logout_user()
    return redirect(url_for("webui.login"))

@login_required
def candidatos(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).first_or_404()   
    candidatos = Candidato.query.filter(Candidato.codigo_municipio == codigo_municipio).order_by(Candidato.percentual_votos_apurados.desc()).all()
    candidatos = ordenar_candidatos(candidatos)
    return render_template("candidatos.html", candidatos=candidatos, municipio=municipio)

@login_required
def criar_video(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).first_or_404()
    candidatos = Candidato.query.filter(Candidato.codigo_municipio == codigo_municipio).order_by(Candidato.votos_apurados).all()
    segundo_turno = True

    # Pega as configurações do template conforme o número de candidatos
    template = pegar_template(len(candidatos))
        
    parameters = {}
    parameters[f"cidade"] = f"{municipio.nome} ({municipio.UF})"        
    
    parameters[f"cidade2"] = f"{municipio.nome} - {municipio.UF}"
    
    candidatos = ordenar_candidatos(candidatos)
    
    for i, candidato in enumerate(candidatos, start=1):
        parameters[f"candidato{i}Nome"] = quebrar_linha(candidato['nome_urna'])
        parameters[f"candidato{i}Partido"] = candidato['partido'] 
        parameters[f"candidato{i}Percentual"] = f"{candidato['percentual_votos_apurados']} %"
        parameters[f"candidato{i}Votos"] = f"{candidato['votos_apurados']} votos"
        parameters[f"candidato{i}Foto"] = f"https://eleicoes.gorobei.net/static/fotos/{candidato['foto']}"
        
    for i, candidato in enumerate(candidatos, start=1):
        if candidato['situacao'] == "Eleito":
            parameters[f"indicadorEleito"] = "100"
            parameters[f"indicador2Turno"] = "0"
            parameters[f"turnoResultado"] = "Não haverá segundo turno"
            segundo_turno = False
            break
        else:
            parameters[f"indicadorEleito"] = "0"
            parameters[f"indicador2Turno"] = "100"
            parameters[f"turnoResultado"] = "Haverá segundo turno"
            segundo_turno = True

    # Abstenções
    parameters[f"abstencaoPercentual"] = f"{municipio.percentual_abstencao} %"
    
    # Brancos e Nulos Percentual
    percentual_votos_nulos_brancos = "{:.2f} %".format(Decimal(municipio.votos_branco) + Decimal(municipio.votos_nulo))
    parameters[f"brancosNulosPercentual"] = f"{percentual_votos_nulos_brancos}"
    
    # Brancos e Nulos Total
    votos_nulos_brancos = Decimal(municipio.votos_branco) + Decimal(municipio.votos_nulo)
    parameters[f"brancosNulosTotal"] = f"{votos_nulos_brancos} votos"
    
    # Votos Válidos
    parameters[f"votosValidos"] = f"Votos válidos {municipio.votos_validos} ({municipio.percentual_votos_validos}%), fonte TSE"
    
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
                "integrationPassthrough": "Teste"
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
    
    video = Video.query.filter_by(video_id = municipio.codigo_municipio).one_or_none()
    yt_copy = gerar_yt_copy(municipio, candidatos, segundo_turno)
    if video:
        video.data_criacao = datetime.datetime.now()
        video.plainly_id = response.json()['id']
        video.plainly_state = response.json()['state']
        video.plainly_template_name=response.json()['projectName']
        video.plainly_template_id=response.json()['projectId']
        video.titulo = yt_copy['titulo']
        video.descricao = yt_copy['descricao']
        video.tag = yt_copy['tags']

    db.session.commit()
    return redirect(url_for('webui.videos'))    

def pegar_template(nm_candidatos):
    templates = [
        {
            'projectId': 'cf6486cb-10ad-4dd9-ab91-2bc9a46ecf8a',
            'templateId': 'dc58120b-4350-44ea-ad65-0044e5bd086d',
            'nm_candidados': 3
        },
        {
            'projectId': '8d34e66a-5fcd-4dc1-a1fa-7237dacf6bbb',
            'templateId': 'c4dad6a1-93d6-48fe-b0c6-859dd5401f60',
            'nm_candidados': 4
        },
        {
            'projectId': '18ab9ede-3dc9-413b-8c6d-bf13f723b59d',
            'templateId': '90e76cbf-9f13-41a2-8ac4-46c82f09dd75',
            'nm_candidados': 5
        },
        {
            'projectId': '0de0f2d5-12ae-48f7-b6ec-4d7bd525bce9',
            'templateId': '35993f2f-f8b2-4daf-afa2-50accb7fe99b',
            'nm_candidados': 6
        },
        {
            'projectId': '113aa2f8-6773-4715-a769-a842bc822dc6',
            'templateId': '78006836-6600-4d2b-b056-83cdf90f10e1',
            'nm_candidados': 7
        },
        {
            'projectId': '67a12862-854f-46a1-8acb-d374b22ec64a',
            'templateId': '832ed4ec-dde5-4fbc-84ec-a0a0d16d3816',
            'nm_candidados': 8
        },
        {
            'projectId': '8decd7f3-0829-4e7b-8235-28efb059037e',
            'templateId': '2dfb8513-76ad-4864-b4e8-da0a20af47be',
            'nm_candidados': 9
        },
        {
            'projectId': 'd4d799dc-cec0-4658-850a-0d00e5f9d5f9',
            'templateId': '63e4b4ab-418e-404e-aa91-08dd0d1ef4de',
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

@login_required
def videos():
    municipios = Municipio.query.order_by(Municipio.totalizacao_final.desc()).all()
    videos = Video.query.order_by(Video.data_criacao.desc()).all()
    return render_template('videos.html', videos=videos, municipios=municipios)

@login_required
def update_video_lista():
    municipios = Municipio.query.order_by(Municipio.totalizacao_final.desc()).all()
    videos = Video.query.order_by(Video.data_criacao.desc()).all()      
    return render_template('partials/_video_lista.html',  videos=videos, municipios=municipios)

@login_required
def update_apuracao_lista():
    municipios = db.session.query(Municipio).order_by(Municipio.totalizacao_final.desc()).all()
    return render_template('partials/_apuracao_lista.html', municipios=municipios)

@login_required
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
    link.text = f"{request.host_url}feed"

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
            item_guid.text = video.video_id

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
            item_media_thumbnail.set("url", f"{request.host_url}static/thumbs/{video.thumbnail_uri}")

    return Response(
        ET.tostring(rss, encoding="utf-8", xml_declaration=True),
        mimetype="application/xml",
    )

def vmix():
    municipios = Municipio.query.all()
    capitais_brasil = [
        "Rio de Janeiro", "São Paulo", "Belo Horizonte", "Vitória",
        "Salvador", "Fortaleza", "Natal", "João Pessoa", "Recife",
        "Maceió", "Aracaju", "Teresina", "Palmas", "São Luís",
        "Belém", "Macapá", "Manaus", "Boa Vista", "Porto Velho",
        "Rio Branco", "Cuiabá", "Campo Grande", "Goiânia", "Curitiba",
        "Florianópolis", "Porto Alegre"
    ]
    data = []
    
    for municipio in municipios:
        if municipio.nome in capitais_brasil:
            item = {
                'cidade': municipio.nome,
                'uf': municipio.UF,
                'percentual_brancos_nulos':"{:.2f} %".format(Decimal(municipio.votos_branco) + Decimal(municipio.votos_nulo)),
                'percentual_secoes_totalizadas':f"{municipio.percentual_secoes_totalizadas} %",
            }
            # Sort candidatos by percentual_votos_apurados in descending order
            sorted_candidatos = sorted(municipio.candidatos, key=lambda c: c.percentual_votos_apurados, reverse=True)
            for num, candidato in enumerate(sorted_candidatos, start=1):
                item[f"candidato_{num}"] = candidato.nome_urna
                item[f"candidato_{num}_partido"] = candidato.partido
                item[f"candidato_{num}_percentual_votos"] = f"{candidato.percentual_votos_apurados}%"
            data.append(item)
    
    return jsonify(data)

@login_required
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

@login_required
def atualizar_apuracao():
    municipios = Municipio.query.all()
    url = "https://p1-cloud.trrsf.com/api/eleicoes2024-api/resultados"
    headers = {
        "Content-Type": "application/json"
    }
    for municipio in municipios:
        params = {
            "municipio": municipio.nome_normalizado
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            apuracao = response.json()['0']
            
            municipio.ht = apuracao['ht']
            municipio.dt = datetime.datetime.strptime(apuracao['dt'], '%d/%m/%Y').date()
            municipio.matematicamente_definido = apuracao['matematicamente_definido'] or 'n'
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
            
            for cand in apuracao['candidatos']:
                candidato = Candidato.query.filter_by(sqcand=cand['sqcand']).one_or_none()
                if candidato:
                    candidato.nro = cand['nro']
                    candidato.seq = cand['seq']
                    candidato.situacao = cand['situacao']
                    candidato.destinacao_voto = cand['destinacao_voto']
                    candidato.votos_apurados = cand['votos_apurados']
                    candidato.percentual_votos_apurados = cand['percentual_votos_apurados']
                    
                    print(candidato)
                else:
                    print(cand['nro'])
                    print(cand['seq'])
                    print(cand['situacao'])
                    print(cand['destinacao_voto'])
                    print(cand['votos_apurados'])
                    print(cand['percentual_votos_apurados'])
                    print(cand)            
    return redirect(url_for('webui.index'))

@login_required
def atualizar_video_status():
    videos = Video.query.filter_by(Video.plainly_state != "DONE", Video.plainly_state != "INVALID").all()
    endpoint = "https://api.plainlyvideos.com/api/v2/renders"
    headers = {
        "Content-Type": "application/json"
    }
    auth = HTTPBasicAuth(current_app.config["PLAINLY_API_KEY"], '')
    for video in videos:
        response = requests.get(
            f"{endpoint}/{video.plainly_id}",
            headers=headers,
            auth=auth
        )
        video.plainly_state = response.json()['state']
        video.plainly_url = response.json()['output']
        db.session.commit()

        response = requests.get(video.plainly_url)

        # Check if videos directory exists
        if not os.path.exists("/app/static/videos"):
            os.makedirs("/app/static/videos")

        with open(f"/app/static/videos/{video.video_id}.mp4", "wb") as f:
            f.write(response.content)
            video.video_uri = f"{video.video_id}.mp4"
            f.close()

        return redirect(url_for('webui.videos'))

@login_required
def yt_copy(codigo_municipio):
    municipio = Municipio.query.filter_by(codigo_municipio=codigo_municipio).one_or_none()
    candidatos = candidatos = Candidato.query.filter(Candidato.codigo_municipio == municipio.codigo_municipio).order_by(Candidato.votos_apurados).all()
    
    candidatos = ordenar_candidatos(candidatos)
    
    segundo_turno = True
    
    for candidato in candidatos:
        if candidato['situacao'] == "Eleito":
            segundo_turno = False
            break
        else:
            segundo_turno = True
            break
    
    yt_copy = gerar_yt_copy(municipio, candidatos, segundo_turno)
    return render_template('copy.html', yt_copy=yt_copy, municipio = municipio)


def gerar_yt_copy(municipio, candidatos, segundo_turno=True):
    
    yt_copy = {}
    
    dias_da_semana = ['nesta Segunda-feira', 'nesta Terça-feira', 'nesta Quarta-feira', 'nesta Quinta-feira', 'nesta Sexta-feira', 'neste Sábado', 'neste Domingo']
    
    titulo = f"Resultado do 1° turno das Eleições 2024 em {municipio.nome}/{municipio.UF}"
    tags = f"{municipio.nome}, Terra Nas Eleições, 1° Turno, Apuração, {municipio.UF}, Eleições Municipais"
    candidatos_tags = []
    
    for candidato in candidatos:
        candidatos_tags.append(f"{candidato['nome_urna'].title()},{candidato['partido']},")
    
    candidatos_tags = ', '.join(candidatos_tags)
    
    tags = candidatos_tags + tags
    
    if segundo_turno:
        descricao = f"""O segundo turno das Eleições 2024 para prefeitura de {municipio.nome.title()}/{municipio.UF} será disputado entre {candidatos[0]['nome_urna'].title()} ({candidatos[0]['partido']}) e {candidatos[1]['nome_urna'].title()} ({candidatos[1]['partido']}). O Tribunal Superior Eleitoral (TSE) concluiu a totalização dos votos do primeiro turno às {municipio.ht} {dias_da_semana[municipio.dt.weekday()]}, {municipio.dt.day}.

Segundo o TSE, com {municipio.percentual_votos_validos}% dos votos válidos e {municipio.percentual_secoes_totalizadas}% das seções apuradas, {candidatos[0]['nome_urna'].title()} teve {candidatos[0]['percentual_votos_apurados']}% ({candidatos[0]['votos_apurados']:,} votos válidos) e {candidatos[1]['nome_urna'].title()}, {candidatos[1]['percentual_votos_apurados']}% ({candidatos[1]['votos_apurados']:,} votos válidos).
    
Os eleitores do município voltarão às urnas no dia 27 de outubro, das 8h às 17h (horário de Brasília), para decidir quem comandará a prefeitura pelos próximos quatros anos.
    
#Eleições2024 #{municipio.nome} #Apuração
    
Aviso: este conteúdo foi gerado automaticamente com base nos dados oficiais do Tribunal Superior Eleitoral (TSE). Informações como nomes, siglas, porcentagens de votos e data do pleito são atualizadas para refletir com precisão os resultados em diferentes municípios. Além disso, o percentual de cada candidato leva em conta os votos de todos os candidatos concorrentes, independente da situação jurídica. Consulte a situação dos candidatos no site do TSE
            
-------------
Inscreva-se no canal do Terra no YouTube ▸ https://www.youtube.com/terra
-------------
Acompanhe as principais notícias do Brasil e do mundo no Terra ▸ https://www.terra.com.br
-------------
Siga o Terra nas redes sociais
Facebook▸ https://www.facebook.com/terrabrasil
Instagram ▸ http://instagram.com/terrabrasil
TikTok ▸ https://www.tiktok.com/@terrabrasil
Twitter ▸ https://twitter.com/terra
WhatsApp ▸ https://whatsapp.com/channel/0029VaDGPXE0rGiN2XvTl03k
"""
            
        
    else:
        descricao = f"""Com {candidatos[0]['percentual_votos_apurados']}% dos votos válidos, {candidatos[0]['nome_urna'].title()} ({candidatos[0]['partido']}) se elegeu à prefeitura de {municipio.nome}/{municipio.UF} no primeiro turno das Eleições 2024. O Tribunal Superior Eleitoral (TSE) concluiu a totalização dos votos do primeiro turno às {municipio.ht} {dias_da_semana[datetime.datetime.now().weekday()]}, {datetime.datetime.now().day}.   
            
Aviso: este conteúdo foi gerado automaticamente com base nos dados oficiais do Tribunal Superior Eleitoral (TSE). Informações como nomes, siglas, porcentagens de votos e data do pleito são atualizadas para refletir com precisão os resultados em diferentes municípios. Além disso, o percentual de cada candidato leva em conta os votos de todos os candidatos concorrentes, independente da situação jurídica. Consulte a situação dos candidatos no site do TSE
            
#Eleições2024 #{municipio.nome} #Apuração
            
-------------
Inscreva-se no canal do Terra no YouTube ▸ https://www.youtube.com/terra
-------------
Acompanhe as principais notícias do Brasil e do mundo no Terra ▸ https://www.terra.com.br
-------------
Siga o Terra nas redes sociais
Facebook▸ https://www.facebook.com/terrabrasil
Instagram ▸ http://instagram.com/terrabrasil
TikTok ▸ https://www.tiktok.com/@terrabrasil
Twitter ▸ https://twitter.com/terra
WhatsApp ▸ https://whatsapp.com/channel/0029VaDGPXE0rGiN2XvTl03k            
"""
    
    yt_copy = {
        'titulo': titulo,
        'tags': tags,
        'descricao': descricao
    }
    
    return yt_copy


def ordenar_candidatos(candidados):
    candidatos_ordendados = []
    for candidato in candidados:
        item = {
            "nro": candidato.nro,
            "seq": candidato.seq,
            "sqcand": candidato.sqcand,
            "situacao": candidato.situacao,
            "destinacao_voto": candidato.destinacao_voto,
            "codigo_municipio": candidato.codigo_municipio,
            "nome_urna": candidato.nome_urna,
            "nome": candidato.nome,
            "foto": candidato.foto,
            "partido": candidato.partido,
            "votos_apurados": Decimal(str(candidato.votos_apurados).replace(".",'')),
            "percentual_votos_apurados": candidato.percentual_votos_apurados
        }
        candidatos_ordendados.append(item)
    # ordenar lista de candidatos por votos_apurados
    candidatos_ordendados = sorted(candidatos_ordendados, key=lambda x: x['votos_apurados'], reverse=True)
    return candidatos_ordendados