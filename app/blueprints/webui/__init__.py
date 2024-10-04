from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import videos
from .webui import criar_video
from .webui import video_lista
from .webui import delete_video
from .webui import criar_feed
from .webui import gerar_todos_os_thumbs
from .webui import terra_json
from .webui import yt_copy
from .webui import download_thumbs
from .webui import atualizar_apuracao

# Register blueprints
bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static")

# Index route
index.methods = ["GET"]
bp.add_url_rule("/", view_func=index)

# Candidatos route
candidatos.methods = ["GET"]
bp.add_url_rule("/candidatos/<codigo_municipio>", view_func=candidatos)

# Criar Video
criar_video.methods = ["GET"]
bp.add_url_rule("/video/criar/<codigo_municipio>", view_func=criar_video)

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

terra_json.methods = ["GET"]
bp.add_url_rule("/terra/<nome_normalizado>", view_func=terra_json)

yt_copy.methods = ["GET"]
bp.add_url_rule("/copy/<codigo_municipio>", view_func=yt_copy)

download_thumbs.methods = ["GET"]
bp.add_url_rule("/thumbs/download", view_func=download_thumbs)

atualizar_apuracao.methods = ["GET"]
bp.add_url_rule("/apuracao", view_func=atualizar_apuracao)

def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
