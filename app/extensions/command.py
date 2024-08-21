import click
import os
import csv

import pandas as pd

from app.extensions.database import db
from app.blueprints.models import Candidato

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

def init_app(app):
    @app.cli.command()
    def import_candidatos():
        csv_file_path = "/home/juliano/apps/app-eleicoes-municipais/csv/consulta_cand_2024/consulta_cand_2024_BRASIL.csv"
        df = pd.read_csv(csv_file_path, sep=";", encoding="ISO-8859-1")
        
        # Filtrar apenas candidatos a prefeito
        df_prefeitos = df[df["DS_CARGO"] == "PREFEITO"]
        
        # Filtrar apenas as colunas que serão importadas para tables candidatos
        df_prefeitos = df_prefeitos[["SQ_CANDIDATO", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_UF", "NM_UE", "NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO", "DS_CARGO"]]  
        
        # Converter df_prefeitos para uma lista de dicionários
        prefeitos = df_prefeitos.to_dict("records")
        for prefeito in prefeitos:
            try:
                candidato = Candidato(
                        sq_canditato=prefeito["SQ_CANDIDATO"],
                        nr_candidato=prefeito["NR_CANDIDATO"],
                        nm_urna_candidato=prefeito["NM_URNA_CANDIDATO"],
                        sg_uf=prefeito["SG_UF"],
                        nm_ue=prefeito["NM_UE"],
                        nr_partido=prefeito["NR_PARTIDO"],
                        sg_partido=prefeito["SG_PARTIDO"],
                        nm_partido=prefeito["NM_PARTIDO"],
                        ds_cargo=prefeito["DS_CARGO"]
                    )
                db.session.add(candidato)
                db.session.commit()
                print(f"Candidato {prefeito['NM_URNA_CANDIDATO']} importado com sucesso.")
            except IntegrityError:
                db.session.rollback()
                print(f"Candidato {prefeito['NM_URNA_CANDIDATO']} já existe no banco de dados.")
                