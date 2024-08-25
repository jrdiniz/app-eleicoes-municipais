import click
import os
import csv
import re
import shutil

import pandas as pd

from app.extensions.database import db
from app.blueprints.models import Candidato
from app.blueprints.models import Municipio

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

def init_app(app):
    @app.cli.command()
    def import_candidatos():
        municipios = db.session.query(Municipio).all()
        
        csv_file_path = "/home/juliano/apps/app-eleicoes-municipais/csv/consulta_cand_2024/consulta_cand_2024_BRASIL.csv"
        df = pd.read_csv(csv_file_path, sep=";", encoding="ISO-8859-1")
        
        # Filtrar apenas candidatos a prefeito
        df_prefeitos = df[df["DS_CARGO"] == "PREFEITO"]
        
        # Filtrar apenas as colunas que serão importadas para tables candidatos
        df_prefeitos = df_prefeitos[["SQ_CANDIDATO", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_UF", "NM_UE", "NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO", "DS_CARGO"]]  
        
        # Converter df_prefeitos para uma lista de dicionários
        prefeitos = df_prefeitos.to_dict("records")
        
        for municipio in municipios:
            for prefeito in prefeitos:
                try:
                    if municipio.nm_ue == prefeito["NM_UE"] and municipio.sg_uf == prefeito["SG_UF"]:
                        candidato = Candidato(
                                sq_canditato=prefeito["SQ_CANDIDATO"],
                                nr_candidato=prefeito["NR_CANDIDATO"],
                                nm_urna_candidato=prefeito["NM_URNA_CANDIDATO"],
                                nr_partido=prefeito["NR_PARTIDO"],
                                sg_partido=prefeito["SG_PARTIDO"],
                                nm_partido=prefeito["NM_PARTIDO"],
                                ds_cargo=prefeito["DS_CARGO"],
                                municipio_id=municipio.id,
                                nr_votos=0,
                                ft_candidato=update_candidatos_fotos(prefeito["SG_UF"], prefeito["SQ_CANDIDATO"])
                            )
                        db.session.add(candidato)
                        db.session.commit()
                        print(f"Candidato {prefeito['NM_URNA_CANDIDATO']} importado com sucesso.")
                except IntegrityError:
                    db.session.rollback()
                    print(f"Candidato {prefeito['NM_URNA_CANDIDATO']} já existe no banco de dados.")
                
                
                
    @app.cli.command()
    def import_candidatos_fotos():
        fotos_file_path = "/home/juliano/apps/app-eleicoes-municipais/fotos/"
        fotos_file_static = "/home/juliano/apps/app-eleicoes-municipais/app/static/fotos/"
        for foto_file in os.listdir(fotos_file_path):
            if foto_file.endswith(('.jpeg','jpg')):
                # Regex para extrair o número do candidato do nome do arquivo da foto
                match = re.search(r'FPE(\d+)_div', foto_file)
                if match:
                    sq_candidato = str(match.group(1)).strip()
                    candidato = Candidato.query.filter_by(sq_candidato=sq_candidato).first()
                    if candidato:
                        candidato.ft_candidato = foto_file.strip() 
                        db.session.commit()
                        # copia a foto para a pasta static de candidatos
                        shutil.copy(fotos_file_path + foto_file, fotos_file_static + foto_file)
                        print(f"Foto do candidato importada com sucesso.")
    
    def update_candidatos_fotos(sg_uf, sg_candidato):
        fotos_file_path = "/home/juliano/apps/app-eleicoes-municipais/app/static/fotos/"
        for foto_file in os.listdir(fotos_file_path):
            foto_file = f"F{sg_uf}{sg_candidato}_div{os.path.splitext(foto_file)[1]}"
            print(foto_file)
            # check if foto_file exists in filesystem
            if os.path.exists(fotos_file_path + foto_file):
                return foto_file
            else:
                return None
               
    @app.cli.command()           
    def update_candidatos_fotos_none():
        fotos_file_path = "/home/juliano/apps/app-eleicoes-municipais/app/static/fotos/"
        candidatos = Candidato.query.filter_by(ft_candidato=None).all()
        for candidato in candidatos:
            ft_candidato = f"F{candidato.municipio.sg_uf}{candidato.sq_candidato}_div.jpeg"
            if os.path.exists(fotos_file_path + ft_candidato):
                print(f"Foto do candidato {candidato.nm_urna_candidato} encontrada, arquivo {ft_candidato}")
                candidato.ft_candidato = ft_candidato
                db.session.commit()
            
            """
            for foto_file in os.listdir(fotos_file_path):
                if os.path.exists(fotos_file_path + ft_candidato):
                    print(f"Foto do candidato {candidato.nm_urna_candidato} encontrada, arquivo {foto_file}")
                    foto_file = update_candidatos_fotos(candidato.municipio.sg_uf, candidato.sq_candidato)
                    candidato.ft_candidato = foto_file
                    db.session.commit()
                else:
                    print(f"Foto do candidato {candidato.nm_urna_candidato} não encontrada.")
            """     
    @app.cli.command()
    def import_municipios():
        municipios_file_path = "/home/juliano/apps/app-eleicoes-municipais/csv/200mil_eleitores_2.csv"
        df = pd.read_csv(municipios_file_path, sep=";", encoding="ISO-8859-1")
        municipios = df.to_dict("records")
        
        for municipio in municipios:
            try:
                data = Municipio(
                        sg_uf=municipio["SG_UF"].upper(),
                        nm_ue=municipio["NM_UE"].upper(),
                        nm_eleitores=municipio["NM_ELEITORES"],
                        nm_nulos_brancos=0,
                        nm_abstencoes=0
                    )
                db.session.add(data)
                db.session.commit()
                print(f"Município {municipio['NM_UE']} importado com sucesso.")
            except IntegrityError:
                db.session.rollback()
                print(f"Município {municipio['NM_UE']} já existe no banco de dados.")
                