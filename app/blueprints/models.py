import uuid
import datetime
from app.extensions.database import db


class Municipio(db.Model):
    __tablename__ = "municipio"
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4().hex),
    )
    
    # Sigla da unidade da federação na qual a candidata ou candidato concorre na eleição.
    sg_uf = db.Column(db.String(2), nullable=False)
    
    # Nome da unidade eleitoral da candidata ou candidato. Em caso de abrangência nacional, é igual a "Brasil". Em caso de abrangência estadual, é o nome da UF em que a candidata ou candidato concorre. Em caso de abrangência municipal, é o nome do município em que a candidata ou candidato concorre.
    nm_ue = db.Column(db.String(255), nullable=False)
    nm_eleitores = db.Column(db.Integer, nullable=False)
    nm_nulos = db.Column(db.Integer, nullable=False, default=0)
    nm_brancos = db.Column(db.Integer, nullable=False, default=0)
    nm_abstencoes = db.Column(db.Integer, nullable=False, default=0)
    status_apuracao = db.Column(db.Boolean, nullable=False, default=False)
    nm_urnas_apuradas = db.Column(db.Numeric(precision=2, scale=2), nullable=False, default=0)

    # Relacionamento Um-Para-Muitos
    candidatos = db.relationship("Candidato", backref="municipio", lazy=True)
    artigos = db.relationship("Artigo", backref="municipio", lazy=True)

    def __init__(self, sg_uf, nm_ue, nm_eleitores, nm_nulos, nm_brancos, nm_abstencoes, status_apuracao, nm_urnas_apuradas):
        self.sg_uf = sg_uf
        self.nm_ue = nm_ue
        self.nm_eleitores = nm_eleitores
        self.nm_nulos = nm_nulos
        self.nm_brancos = nm_brancos
        self.nm_abstencoes = nm_abstencoes
        self.status_apuracao = status_apuracao
        self.nm_urnas_apuradas = nm_urnas_apuradas


class Candidato(db.Model):
    __tablename__ = "candidato"
    
    # Número sequencial da candidata ou candidato, gerado internamente pelos sistemas eleitorais para cada eleição. Observação: não é o número de campanha da candidata ou candidato.
    sq_candidato = db.Column(db.String(12), primary_key=True, nullable=False, index=True, unique=True)
    
    # Número da candidata ou candidato na urna.
    nr_candidato = db.Column(db.Integer, nullable=False)
    
    # Nome da candidata ou candidato que aparece na urna.
    nm_urna_candidato = db.Column(db.String(255), nullable=False)
    
    # Número do partido da candidata ou candidato.
    nr_partido = db.Column(db.Integer, nullable=False)
    
    # Sigla do partido da candidata ou candidato.
    sg_partido = db.Column(db.String(50), nullable=False)
    
    # Nome do partido da candidata ou candidato.
    nm_partido = db.Column(db.String(255), nullable=False)
    
    # Descrição do cargo ao qual a candidata ou candidato concorre.
    ds_cargo = db.Column(db.String(100), nullable=False)
    
    # Nome do arquivos de foto
    ft_candidato = db.Column(db.String(255), nullable=True, default=None) 
    
    # Total de votos do candidato
    nr_votos = db.Column(db.Integer, nullable=False, default=0)
    
    municipio_id = db.Column(db.String(36), db.ForeignKey("municipio.id"), nullable=False)
    
    def __init__(self, sq_canditato, nr_candidato, nm_urna_candidato, nr_partido, sg_partido, nm_partido, ds_cargo, ft_candidato, nr_votos, municipio_id):
        self.sq_candidato = sq_canditato
        self.nr_candidato = nr_candidato
        self.nm_urna_candidato = nm_urna_candidato
        self.nr_partido = nr_partido
        self.sg_partido = sg_partido
        self.nm_partido = nm_partido
        self.ds_cargo = ds_cargo
        self.ft_candidato = ft_candidato
        self.nr_votos = nr_votos
        self.municipio_id = municipio_id
    
class Artigo(db.Model):
    __tablename__ = "artigo"

    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4().hex),
    )
    titulo = db.Column(db.String(255), nullable=False)
    subtitulo = db.Column(db.String(255), nullable=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    
    municipio_id = db.Column(db.String(36), db.ForeignKey("municipio.id"), nullable=False)

    def __init__(self, titulo, subtitulo, thumbnail, conteudo, municipio_id):
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.thumbnail = thumbnail
        self.conteudo = conteudo
        self.municipio_id = municipio_id
