import csv
import requests

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


def criar_thumbnail(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()
    options = {
        # The ID of the template that you created in the template editor
        'template_id': '6c4ce658-a53f-406e-b037-d2a84dc0b927',

        # Modifications that you want to apply to the template
            'modifications': {
                'Municipio': f"Prefeitura de {municipio.nm_ue.title()}",
            },
    }

    response = requests.post('https://api.creatomate.com/v1/renders',
        headers={
            'Authorization': f"Bearer {current_app.config['CREATOMATE_API_KEY']}",
            'Content-Type': 'application/json',
        },
        json=options
    )
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()
    return render_template('thumbnail.html', image_url=response.json()[0]['url'], municipio=municipio)