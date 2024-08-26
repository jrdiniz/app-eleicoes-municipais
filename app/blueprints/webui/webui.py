import csv

from flask import Flask
from flask import request
from flask import Response
from flask import render_template
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

def artigo():
    return render_template("artigo.html")


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
            row.extend([
                candidato.nr_candidato,
                candidato.nm_urna_candidato,
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
