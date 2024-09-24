from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import videos
from .webui import criar_artigo
from .webui import export_to_csv
from .webui import criar_video
from .webui import video_lista
from .webui import delete_video
from .webui import criar_feed
from .webui import gerar_todos_os_thumbs
from .webui import thumbs

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

delete_video.methods = ["GET"]
bp.add_url_rule("/video/delete/<video_id>", view_func=delete_video)

criar_feed.methods = ["GET"]
bp.add_url_rule("/feed", view_func=criar_feed)

gerar_todos_os_thumbs.methods = ["GET"]
bp.add_url_rule("/thumbs", view_func=gerar_todos_os_thumbs)

thumbs.methods = ["GET"]
bp.add_url_rule("/thumbs/lista", view_func=thumbs)

def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
