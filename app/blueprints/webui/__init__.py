from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import videos
from .webui import criar_artigo
from .webui import export_to_csv
from .webui import criar_video
from .webui import video_lista
from .webui import tse

# Register blueprints
bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static")

# Index route
index.methods = ["GET"]
bp.add_url_rule("/", view_func=index)

# Candidatos route
candidatos.methods = ["GET"]
bp.add_url_rule("/candidatos/<municipio_id>", view_func=candidatos)

# Artigo
criar_artigo.methods = ["GET"]
bp.add_url_rule("/artigo/<municipio_id>", view_func=criar_artigo)

# Export CSV
export_to_csv.methods = ["GET"]
bp.add_url_rule("/export_csv", view_func=export_to_csv)

# Cirar Video
criar_video.methods = ["GET"]
bp.add_url_rule("/video/criar/<municipio_id>", view_func=criar_video)

# Lista de Vídeos Criados
videos.methods = ["GET"]
bp.add_url_rule("/videos", view_func=videos)

# Updade Plainly State
video_lista.methods = ["GET"]
bp.add_url_rule("/video/lista", view_func=video_lista)

# TSE Test
tse.methods = ["GET"]
bp.add_url_rule("/tse", view_func=tse)


def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
