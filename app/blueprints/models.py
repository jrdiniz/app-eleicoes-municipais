import uuid
import datetime
from app.extensions.database import db


class Municipio(db.Model):
    __tablename__ = 'municipios'

    codigo_municipio = db.Column(db.String(10), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_normalizado = db.Column(db.String(100), nullable=False)
    UF = db.Column(db.String(2), nullable=False)
    dt = db.Column(db.Date, nullable=False, default=datetime.date.today)
    ht = db.Column(db.Time, nullable=False, default=datetime.datetime.now().time()
    matematicamente_definido = db.Column(db.String(1), nullable=False)
    totalizacao_final = db.Column(db.String(1), nullable=False)
    total_votos = db.Column(db.String(20), nullable=False)
    votos_validos = db.Column(db.String(20), nullable=False)
    percentual_votos_validos = db.Column(db.String(20), nullable=False)
    percentual_secoes_totalizadas = db.Column(db.String(20), nullable=False)
    votos_branco = db.Column(db.String(20), nullable=False)
    percentual_votos_branco = db.Column(db.String(20), nullable=False)
    votos_nulo = db.Column(db.String(20), nullable=False)
    percentual_votos_nulo = db.Column(db.String(20), nullable=False)
    abstencao = db.Column(db.String(20), nullable=False)
    percentual_abstencao = db.Column(db.String(20), nullable=False)

    # Relationship with Candidatos (one-to-many)
    candidatos = db.relationship('Candidato', backref='municipio', lazy=True)
    videos = db.relationship('Video', backref='municipio', lazy=True)


class Candidato(db.Model):
    __tablename__ = 'candidatos'
    nro = db.Column(db.String(10), nullable=False)  # Candidate number
    seq = db.Column(db.String(10), nullable=True)  # Sequence
    sqcand = db.Column(db.String(20), primary_key=True, nullable=False)  # Unique candidate identifier
    situacao = db.Column(db.String(100), nullable=True)  # Status
    destinacao_voto = db.Column(db.String(20), nullable=True)  # Vote destination
    nome_urna = db.Column(db.String(100), nullable=False)  # Name on ballot
    nome = db.Column(db.String(100), nullable=False)  # Full name
    foto = db.Column(db.String(255), nullable=True)  # Candidate photo URL
    partido = db.Column(db.String(50), nullable=False)  # Party affiliation
    votos_apurados = db.Column(db.String(20), nullable=True)  # Count of votes
    percentual_votos_apurados = db.Column(db.String(20), nullable=True)  # Percent of votes

    # Foreign key to Municipio
    codigo_municipio = db.Column(db.String(10), db.ForeignKey('municipios.codigo_municipio'), nullable=False)

    
class Video(db.Model):
    __tablename__ = "video"

    video_id = db.Column(db.String(10), primary_key=True) # codigo_municipio
    titulo = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    thumbnail_uri = db.Column(db.Text, nullable=True)
    video_uri = db.Column(db.Text, nullable=True)
    plainly_id = db.Column(db.String(36), nullable=True)
    plainly_url = db.Column(db.Text, nullable=True)
    plainly_state = db.Column(db.String(25), nullable=True)
    plainly_template_name = db.Column(db.String(255), nullable=True)
    plainly_template_id = db.Column(db.String(255), nullable=True)
    plainly_thumbnail_uri = db.Column(db.Text, nullable=True)
    plainly_thumbnail_id = db.Column(db.Text, nullable=True)
    plainly_thumbnail_state = db.Column(db.String(25), nullable=True)
    
    # Foreign key to Municipio
    codigo_municipio = db.Column(db.String(10), db.ForeignKey('municipios.codigo_municipio'), nullable=False)
    
    
        
class Thumb(db.Model):
    __tablename__ = "thumb"
    id = db.Column(db.String(36), primary_key=True, nullable=False, unique=True, index=True, default=lambda: str(uuid.uuid4().hex))
    plainly_thumbnail_uri = db.Column(db.Text, nullable=False)
    plainly_id = db.Column(db.String(36), nullable=True)
    plainly_state = db.Column(db.String(25), nullable=True)
    municipio_id = db.Column(db.String(35), nullable=False, index=True)
    
    def __init__(self, plainly_thumbnail_uri, plainly_id, plainly_state, municipio_id):
        self.plainly_thumbnail_uri = plainly_thumbnail_uri
        self.plainly_id = plainly_id
        self.plainly_state = plainly_state
        self.municipio_id = municipio_id