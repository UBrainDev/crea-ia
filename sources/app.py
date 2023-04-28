import os
from flask_socketio import SocketIO

from flask import Flask, g


def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,
                template_folder='src/templates', static_folder='src/static')
    app.config.from_mapping(
        SECRET_KEY=os.urandom(16).hex(),
        DATABASE=os.path.join(app.instance_path, 'crea_ia.sqlite'),
    )

    # créer le dossier d'instance s'il n'existe pas
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # enregistrer les blueprints
    from src.blueprints import models, api
    for bp in [models, api]:
        app.register_blueprint(bp.bp)

    # initialiser la base de données
    from src import db
    db.init_app(app)

    # serveur websocket
    socketio = SocketIO(app)
    with app.app_context():
        g.ws = socketio

    # démarrer le serveur websocket
    if __name__ == '__main__':
        socketio.run(app)

    # enregistrer les écouteurs d'évènements websocket
    from src.interne import train
    train.register_ws_events(socketio)

    # rediriger la racine vers la page des modèles
    @app.route('/')
    def index():
        return models.index()

    return app
