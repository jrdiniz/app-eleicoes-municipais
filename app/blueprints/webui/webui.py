from flask import Flask
from flask import request
from flask import render_template

from app.blueprints.models import Candidato
from app.blueprints.models import Municipio
from app.extensions.database import db

# SQLAlchemy
from sqlalchemy import func


def index():
    municipios = db.session.query(Municipio.id, Municipio.nm_ue, Municipio.sg_uf, Municipio.nm_eleitores, Municipio.nm_abstencoes, Municipio.nm_nulos_brancos, func.count(Candidato.sq_candidato).label('nm_candidatos')).join(Candidato).group_by(Municipio.id).order_by(Municipio.nm_eleitores.desc()).all()
    return render_template("index.html", municipios=municipios)

def candidatos(municipio_id):
    municipio = Municipio.query.filter_by(id=municipio_id).first_or_404()   
    candidatos = Candidato.query.filter(Candidato.municipio_id == municipio_id).all()
    return render_template("candidatos.html", candidatos=candidatos, municipio=municipio)

def artigo():
    return render_template("artigo.html")

def prefeitos():
    
    municipios = db.session.query(Candidato.nm_ue).order_by(Candidato.nm_ue.asc()).distinct().all()
    municipios = [municipio[0] for municipio in municipios]
    
    estados = db.session.query(Candidato.sg_uf).order_by(Candidato.sg_uf.asc()).distinct().all()
    estados = [estado[0] for estado in estados]
    
    return render_template("prefeitos.html", municipios=municipios, estados=estados)


def filtro_prefeitos_por_estado_municipio(): 
    if request.method == "POST":    
        nm_ue = request.form.get("nm_ue")
        sg_uf = request.form.get("sg_uf")
    
        prefeitos = Candidato.query.filter_by(nm_ue=nm_ue, sg_uf=sg_uf).all()
        return render_template("partials/_filtro_prefeito_municipio_estado.html", prefeitos=prefeitos)
    
    
def filtro_municipios_por_estado():
    sg_uf = request.args.get('sg_uf')
    municipios = db.session.query(Candidato.nm_ue).filter(Candidato.sg_uf==sg_uf).order_by(Candidato.nm_ue.asc()).distinct().all()
    municipios = [municipio[0] for municipio in municipios]
    return render_template("partials/_filtro_municipios_por_estado.html", municipios=municipios)