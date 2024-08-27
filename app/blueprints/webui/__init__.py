from flask import Blueprint

# Import routes
from .webui import index
from .webui import candidatos
from .webui import criar_artigo
from .webui import export_to_csv
from .webui import criar_thumbnail

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

# Gerar Thumbnail
criar_thumbnail.methods = ["GET"]
bp.add_url_rule("/criar_thumbnail/<municipio_id>", view_func=criar_thumbnail)


def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
