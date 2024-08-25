from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import prefeitos
from .webui import artigo
from .webui import filtro_prefeitos_por_estado_municipio
from .webui import filtro_municipios_por_estado

# Register blueprints
bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static")

# Index route
index.methods = ["GET"]
bp.add_url_rule("/", view_func=index)

# Candidatos route
candidatos.methods = ["GET"]
bp.add_url_rule("/candidatos/<municipio_id>", view_func=candidatos)

# Prefeitos route
prefeitos.methods = ["GET"]
bp.add_url_rule("/prefeitos", view_func=prefeitos)

# Artigo
artigo.methods = ["GET"]
bp.add_url_rule("/artigo", view_func=artigo)

# Filtrar route
filtro_prefeitos_por_estado_municipio.methods = ["POST"]
bp.add_url_rule("/prefeitos/filtros", view_func=filtro_prefeitos_por_estado_municipio)

# Filtrar Municipios por Estado
filtro_municipios_por_estado.methods = ["GET"]
bp.add_url_rule("/municipios", view_func=filtro_municipios_por_estado)


def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
