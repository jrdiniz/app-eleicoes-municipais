from flask import Flask
from flask import render_template

from app.blueprints.models import Candidato
from app.extensions.database import db


def index():
    return render_template("index.html")


def prefeitos():
    
    municipios = db.session.query(Candidato.nm_ue).order_by(Candidato.nm_ue.asc()).distinct().all()
    municipios = [municipio[0] for municipio in municipios]
    
    estados = db.session.query(Candidato.sg_uf).order_by(Candidato.sg_uf.asc()).distinct().all()
    estados = [estado[0] for estado in estados]
    
    partidos = db.session.query(Candidato.sg_partido).order_by(Candidato.sg_partido.asc()).distinct().all()
    partidos = [partido[0] for partido in partidos]
    
    prefeitos = Candidato.query.filter_by(ds_cargo="PREFEITO").all()
    return render_template("prefeitos.html", prefeitos=prefeitos, municipios=municipios, estados=estados, partidos=partidos)
