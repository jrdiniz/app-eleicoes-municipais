import uuid
import datetime
from app.extensions.database import db


class Candidato(db.Model):
    __tablename__ = "candidatos"
    
    # Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. Observação: não é o número de campanha da candidata ou candidato.
    sq_candidato = db.Column(db.String(12), primary_key=True, nullable=False)
    
    # Número da candidata ou candidato na urna.
    nr_candidato = db.Column(db.Integer, nullable=False)
    
    # Nome da candidata ou candidato que aparece na urna.
    nm_urna_candidato = db.Column(db.String(255), nullable=False)
    
    # Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição.
    sg_uf = db.Column(db.String(2), nullable=False)
    
    # Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal, é o nome do município em que a candidata ou candidato concorre.
    nm_ue = db.Column(db.String(255), nullable=False)
    
    # Número do partido da candidata ou candidato.
    nr_partido = db.Column(db.Integer, nullable=False)
    
    # Sigla do partido da candidata ou candidato.
    sg_partido = db.Column(db.String(50), nullable=False)
    
    # Nome do partido da candidata ou candidato.
    nm_partido = db.Column(db.String(255), nullable=False)
    
    # Descrição do cargo ao qual a candidata ou candidato concorre.
    ds_cargo = db.Column(db.String(100), nullable=False)
 
    def __init__(self, sq_canditato, nr_candidato, nm_urna_candidato, sg_uf, nm_ue, nr_partido, sg_partido, nm_partido, ds_cargo):
        self.sq_candidato = sq_canditato
        self.nr_candidato = nr_candidato
        self.nm_urna_candidato = nm_urna_candidato
        self.sg_uf = sg_uf
        self.nm_ue = nm_ue
        self.nr_partido = nr_partido
        self.sg_partido = sg_partido
        self.nm_partido = nm_partido
        self.ds_cargo = ds_cargo
    