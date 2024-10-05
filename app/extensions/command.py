import click
import os
import re
import unidecode
import requests
import json
import csv
from datetime import datetime

import pandas as pd

from app.extensions.database import db
from app.blueprints.models import Candidato
from app.blueprints.models import Municipio

from datetime import datetime

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

def init_app(app):
    @app.cli.command()
    def update_municipios():
        municipios = [
            {'nome': 'Rio Branco', 'uf': 'AC'},
            {'nome': 'Maceió', 'uf': 'AL'},
            {'nome': 'Manaus', 'uf': 'AM'},
            {'nome': 'Macapá', 'uf': 'AP'},
            {'nome': 'Salvador', 'uf': 'BA'},
            {'nome': 'Feira de Santana', 'uf': 'BA'},
            {'nome': 'Vitória da Conquista', 'uf': 'BA'},
            {'nome': 'Camaçari', 'uf': 'BA'},
            {'nome': 'Fortaleza', 'uf': 'CE'},
            {'nome': 'Caucaia', 'uf': 'CE'},
            {'nome': 'Serra', 'uf': 'ES'},
            {'nome': 'Vila Velha', 'uf': 'ES'},
            {'nome': 'Cariacica', 'uf': 'ES'},
            {'nome': 'Vitória', 'uf': 'ES'},
            {'nome': 'Goiânia', 'uf': 'GO'},
            {'nome': 'Aparecida de Goiânia', 'uf': 'GO'},
            {'nome': 'Anápolis', 'uf': 'GO'},
            {'nome': 'São Luís', 'uf': 'MA'},
            {'nome': 'Imperatriz', 'uf': 'MA'},
            {'nome': 'Belo Horizonte', 'uf': 'MG'},
            {'nome': 'Uberlândia', 'uf': 'MG'},
            {'nome': 'Contagem', 'uf': 'MG'},
            {'nome': 'Juiz de Fora', 'uf': 'MG'},
            {'nome': 'Betim', 'uf': 'MG'},
            {'nome': 'Montes Claros', 'uf': 'MG'},
            {'nome': 'Uberaba', 'uf': 'MG'},
            {'nome': 'Ribeirão das Neves', 'uf': 'MG'},
            {'nome': 'Campo Grande', 'uf': 'MS'},
            {'nome': 'Cuiabá', 'uf': 'MT'},
            {'nome': 'Belém', 'uf': 'PA'},
            {'nome': 'Ananindeua', 'uf': 'PA'},
            {'nome': 'Santarém', 'uf': 'PA'},
            {'nome': 'João Pessoa', 'uf': 'PB'},
            {'nome': 'Campina Grande', 'uf': 'PB'},
            {'nome': 'Recife', 'uf': 'PE'},
            {'nome': 'Jaboatão dos Guararapes', 'uf': 'PE'},
            {'nome': 'Olinda', 'uf': 'PE'},
            {'nome': 'Caruaru', 'uf': 'PE'},
            {'nome': 'Petrolina', 'uf': 'PE'},
            {'nome': 'Paulista', 'uf': 'PE'},
            {'nome': 'Teresina', 'uf': 'PI'},
            {'nome': 'Curitiba', 'uf': 'PR'},
            {'nome': 'Londrina', 'uf': 'PR'},
            {'nome': 'Maringá', 'uf': 'PR'},
            {'nome': 'Ponta Grossa', 'uf': 'PR'},
            {'nome': 'Cascavel', 'uf': 'PR'},
            {'nome': 'São José dos Pinhais', 'uf': 'PR'},
            {'nome': 'Foz do Iguaçu', 'uf': 'PR'},
            {'nome': 'Rio de Janeiro', 'uf': 'RJ'},
            {'nome': 'Duque de Caxias', 'uf': 'RJ'},
            {'nome': 'São Gonçalo', 'uf': 'RJ'},
            {'nome': 'Nova Iguaçu', 'uf': 'RJ'},
            {'nome': 'Niterói', 'uf': 'RJ'},
            {'nome': 'São João de Meriti', 'uf': 'RJ'},
            {'nome': 'Campos dos Goytacazes', 'uf': 'RJ'},
            {'nome': 'Belford Roxo', 'uf': 'RJ'},
            {'nome': 'Petrópolis', 'uf': 'RJ'},
            {'nome': 'Volta Redonda', 'uf': 'RJ'},
            {'nome': 'Magé', 'uf': 'RJ'},
            {'nome': 'Natal', 'uf': 'RN'},
            {'nome': 'Porto Velho', 'uf': 'RO'},
            {'nome': 'Boa Vista', 'uf': 'RR'},
            {'nome': 'Porto Alegre', 'uf': 'RS'},
            {'nome': 'Caxias do Sul', 'uf': 'RS'},
            {'nome': 'Canoas', 'uf': 'RS'},
            {'nome': 'Pelotas', 'uf': 'RS'},
            {'nome': 'Santa Maria', 'uf': 'RS'},
            {'nome': 'Joinville', 'uf': 'SC'},
            {'nome': 'Florianópolis', 'uf': 'SC'},
            {'nome': 'Blumenau', 'uf': 'SC'},
            {'nome': 'Aracaju', 'uf': 'SE'},
            {'nome': 'Barueri', 'uf': 'SP'},
            {'nome': 'Bauru', 'uf': 'SP'},
            {'nome': 'Campinas', 'uf': 'SP'},
            {'nome': 'Carapicuíba', 'uf': 'SP'},
            {'nome': 'Diadema', 'uf': 'SP'},
            {'nome': 'Embu das Artes', 'uf': 'SP'},
            {'nome': 'Franca', 'uf': 'SP'},
            {'nome': 'Guarujá', 'uf': 'SP'},
            {'nome': 'Guarulhos', 'uf': 'SP'},
            {'nome': 'Itaquaquecetuba', 'uf': 'SP'},
            {'nome': 'Jundiaí', 'uf': 'SP'},
            {'nome': 'Limeira', 'uf': 'SP'},
            {'nome': 'Mauá', 'uf': 'SP'},
            {'nome': 'Mogi das Cruzes', 'uf': 'SP'},
            {'nome': 'Osasco', 'uf': 'SP'},
            {'nome': 'Piracicaba', 'uf': 'SP'},
            {'nome': 'Praia Grande', 'uf': 'SP'},
            {'nome': 'Ribeirão Preto', 'uf': 'SP'},
            {'nome': 'Santo André', 'uf': 'SP'},
            {'nome': 'Santos', 'uf': 'SP'},
            {'nome': 'São Bernardo do Campo', 'uf': 'SP'},
            {'nome': 'São José do Rio Preto', 'uf': 'SP'},
            {'nome': 'São José dos Campos', 'uf': 'SP'},
            {'nome': 'São Paulo', 'uf': 'SP'},
            {'nome': 'São Vicente', 'uf': 'SP'},
            {'nome': 'Sorocaba', 'uf': 'SP'},
            {'nome': 'Sumaré', 'uf': 'SP'},
            {'nome': 'Suzano', 'uf': 'SP'},
            {'nome': 'Taboão da Serra', 'uf': 'SP'},
            {'nome': 'Taubaté', 'uf': 'SP'},
            {'nome': 'Palmas', 'uf': 'TO'}
        ]
        url = "https://p1-cloud.trrsf.com/api/eleicoes2024-api/resultados"
        for municipio in municipios:
            normalize = unidecode.unidecode(municipio['nome'])
            municipio['nome_normalizado'] = normalize.upper()
            
            
            # Request API 
            params = {
                "municipio": municipio['nome_normalizado']
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()['0']
                result = Municipio.query.filter_by(codigo_municipio=data['codigo_municipio']).first()   
                if result is None:
                    apuracao = response.json()['0']
                    try:
                        apuracao_data = apuracao['ht']
                        apuracao_time = datetime.datetime.strptime(apuracao['dt'], '%d/%m/%Y').date()
                    except Exception as e:
                        apuracao_data = datetime.datetime.now().date()
                        apuracao_time = datetime.datetime.now().time()   
                    
                    new_municipio = Municipio(
                        codigo_municipio=data['codigo_municipio'],
                        nome=data['nome'], 
                        nome_normalizado=data['nome_normalizado'],
                        UF=data['UF'],
                        dt=apuracao_data,
                        ht=apuracao_time,
                        matematicamente_definido=data['matematicamente_definido'],
                        totalizacao_final=data['totalizacao_final'],
                        total_votos=data['total_votos'],
                        votos_validos=data['votos_validos'],
                        percentual_votos_validos=data['percentual_votos_validos'],
                        percentual_secoes_totalizadas=data['percentual_secoes_totalizadas'],
                        votos_branco=data['votos_branco'],
                        percentual_votos_branco=data['percentual_votos_branco'],
                        votos_nulo=data['votos_nulo'],
                        percentual_votos_nulo=data['percentual_votos_nulo'],
                        abstencao=data['abstencao'],
                        percentual_abstencao=data['percentual_abstencao'],
                    )        
                    db.session.add(new_municipio)
                    for candidato_data in data['candidatos']:
                        
                        # check if foto exist in static/fotos
                        candidato_foto = ""
                        if os.path.exists(f"static/fotos/{result.UF}{candidato_data['sqcand']}_div.jpg"):
                            candidato_foto = f"{result.UF}{candidato_data['sqcand']}_div.jpg"
                        elif os.path.exists(f"static/fotos/{result.UF}{candidato_data['sqcand']}_div.jpeg"):
                            candidato_foto = f"{result.UF}{candidato_data['sqcand']}_div.jpeg"
                        else:
                            print(f"Foto não encontrada {result.UF}{candidato_data['sqcand']}")
                            
                        candidato = Candidato(
                            nro=candidato_data['nro'],
                            seq=candidato_data['seq'],
                            sqcand=candidato_data['sqcand'],
                            situacao=candidato_data.get('situacao', ''),  # Optional field, default to empty string if missing
                            destinacao_voto=candidato_data['destinacao_voto'],
                            nome_urna=candidato_data['nome_urna'],
                            nome=candidato_data['nome'],
                            foto=candidato_foto,
                            partido=candidato_data['partido'],
                            votos_apurados=candidato_data['votos_apurados'],
                            percentual_votos_apurados=candidato_data['percentual_votos_apurados'],
                            codigo_municipio=new_municipio.codigo_municipio  # Foreign key relationship
                        )
                        # Add each Candidato to the session
                        db.session.add(candidato)
                else:
                    result.nome = data['nome']
                    result.nome_normalizado = data['nome_normalizado']
                    result.UF = data['UF']
                    result.matematicamente_definido = data['matematicamente_definido']
                    result.totalizacao_final = data['totalizacao_final']
                    result.total_votos = data['total_votos']
                    result.votos_validos = data['votos_validos']
                    result.percentual_votos_validos = data['percentual_votos_validos']
                    result.percentual_secoes_totalizadas = data['percentual_secoes_totalizadas']
                    result.votos_branco = data['votos_branco']
                    result.percentual_votos_branco = data['percentual_votos_branco']
                    result.votos_nulo = data['votos_nulo']
                    result.percentual_votos_nulo = data['percentual_votos_nulo']
                    result.abstencao = data['abstencao']
                    result.percentual_abstencao = data['percentual_abstencao']
                    
                    for candidato in result.candidatos:
                        # check if foto exist in static/fotos
                        candidato_foto = ""
                        if os.path.exists(f"static/fotos/{result.UF}{candidato.sqcand}_div.jpg"):
                            candidato_foto = f"{result.UF}{candidato.sqcand}_div.jpg"
                        elif os.path.exists(f"static/fotos/{result.UF}{candidato.sqcand}_div.jpeg"):
                            candidato_foto = f"{result.UF}{candidato.sqcand}_div.jpeg"
                        else:
                            print(f"Foto não encontrada {result.UF}{candidato.sqcand}_div")
                        candidato.foto = candidato_foto
                db.session.commit()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
                
    @app.cli.command()
    def import_candidatos():
        municipios = db.session.query(Municipio).all()

        csv_file_path = "/home/juliano/apps/app-eleicoes-municipais/csv/consulta_cand_2024/consulta_cand_2024_BRASIL.csv"
        df = pd.read_csv(csv_file_path, sep=";", encoding="ISO-8859-1")

        # Filtrar apenas candidatos a prefeito
        df_prefeitos = df[df["DS_CARGO"] == "PREFEITO"]

        # Filtrar apenas as colunas que serão importadas para tables candidatos
        df_prefeitos = df_prefeitos[["SQ_CANDIDATO", "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_UF", "NM_UE", "NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO", "DS_CARGO"]]

        # Converter df_prefeitos para uma lista de dicionários
        prefeitos = df_prefeitos.to_dict("records")

        # Fotos
        fotos_file_path = "/home/juliano/apps/app-eleicoes-municipais/app/static/fotos/"

        for municipio in municipios:
            for prefeito in prefeitos:
                try:
                    if municipio.nome.upper() == prefeito["NM_UE"] and municipio.UF == prefeito["SG_UF"]:
                        candidato = {
                            "sqcand": prefeito['SQ_CANDIDATO'],
                            "nro": prefeito['NR_CANDIDATO'],
                            "nome_urna": prefeito['NM_URNA_CANDIDATO'],
                            "nome": prefeito['NM_CANDIDATO'],
                            "partido": f"{prefeito['SG_PARTIDO']}",
                            "votos_apurados": str(0),
                            "percentual_votos_apurados": str(0.0),
                            "seq": str(0)
                        }
                        # Get photo from app/static/fotos
                        ft_candidato = f"F{municipio.UF}{candidato['sqcand']}_div"
                        if os.path.exists(fotos_file_path + f"{ft_candidato}.jpeg"):
                            candidato['foto'] = f"{ft_candidato}.jpeg"
                        elif os.path.exists(fotos_file_path + f"{ft_candidato}.jpg"):
                            candidato['foto'] = f"{ft_candidato}.jpg"
                        else:
                            candidato['foto'] = "none.jpeg"
                            
                        data = Candidato(**candidato, codigo_municipio=municipio.codigo_municipio)
                        db.session.add(data)
                        db.session.commit()
                        print(f"Candidato {candidato} importado com sucesso.")
                except IntegrityError:
                    db.session.rollback()
                    print(f"Candidato {prefeito['NM_URNA_CANDIDATO']} já existe no banco de dados.")


    @app.cli.command()
    def clean_municipios_variables():
        municipios = db.session.query(Municipio).all()
        for municipio in municipios:
            municipio.totalizacao_final = 'n'
            municipio.total_votos = str(0)
            municipio.votos_validos = str(0)
            municipio.percentual_votos_validos = str(0)
            municipio.percentual_secoes_totalizadas = str(0)
            municipio.votos_branco = str(0)
            municipio.percentual_votos_branco = str(0)
            municipio.votos_nulo = str(0)
            municipio.percentual_votos_nulo = str(0)
            municipio.abstencao = str(0)
            municipio.percentual_abstencao = str(0)
            municipio.matematicamente_definido = 'n'
            municipio.ht = datetime.now().time()
            municipio.dt = datetime.now().date()
            db.session.commit()
            print(f"Valores variaveis zerados {municipio.nome}")
            
            
    @app.cli.command()
    def clean_candidatos_variables():
        candidatos = db.session.query(Candidato).all()
        for candidato in candidatos:
            candidato.votos_apurados = str(0)
            candidato.percentual_votos_apurados = str(0.0)
            candidato.seq = str(0)
            candidato.situacao = ''
            candidato.destinacao_voto = ''
            db.session.commit()
            print(f"Valores variaveis zerados {candidato.nome}")
        