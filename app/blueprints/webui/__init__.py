from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import videos
from .webui import criar_video
from .webui import update_video_lista
from .webui import update_apuracao_lista
from .webui import delete_video
from .webui import criar_feed
from .webui import terra_json
from .webui import yt_copy
from .webui import atualizar_apuracao
from .webui import vmix

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

delete_video.methods = ["GET"]
bp.add_url_rule("/video/delete/<video_id>", view_func=delete_video)

criar_feed.methods = ["GET"]
bp.add_url_rule("/feed", view_func=criar_feed)

terra_json.methods = ["GET"]
bp.add_url_rule("/terra/<nome_normalizado>", view_func=terra_json)

yt_copy.methods = ["GET"]
bp.add_url_rule("/copy/<codigo_municipio>", view_func=yt_copy)

atualizar_apuracao.methods = ["GET"]
bp.add_url_rule("/apuracao", view_func=atualizar_apuracao)

update_video_lista.methods = ["GET"]
bp.add_url_rule("/video/update", view_func=update_video_lista)

update_apuracao_lista.methods = ["GET"]
bp.add_url_rule("/apuracao/update", view_func=update_apuracao_lista)

vmix.methods = ["GET"]
bp.add_url_rule("/vmix", view_func=vmix)

def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
