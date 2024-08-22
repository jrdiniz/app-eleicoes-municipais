from flask import Flask
from flask import request
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