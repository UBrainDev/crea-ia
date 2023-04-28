import json
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from src.db import get_db
import os

bp = Blueprint('models', __name__, url_prefix='/models')


def get_model(id):
    """
    Retourne le modèle demandé dans la base de données
    """
    db = get_db()
    model = db.execute('SELECT * FROM models WHERE id = ?', (id,)).fetchone()
    return model


@bp.route('/')
def index():
    """
    Liste des modèles disponibles
    """
    db = get_db()
    models = db.execute('SELECT * FROM models').fetchall()

    # si aucun modèle n'est repertorié
    if len(models) == 0:
        return render_template('models/intro.html', id=None)
    return render_template('models/index.html', models=models)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    """
    Formulaire de création d'un nouveau modèle
    """
    if request.method == 'POST':
        print(request.form['nom'])
        print(request.form)
        name = request.form['nom']
        type = int(request.form['type'])
        db = get_db()
        db.execute('INSERT INTO models (nom, type) VALUES (?, ?)', (name, type))
        db.commit()
        return redirect(url_for('models.index'))
    return render_template('models/create.html')

@bp.route('/<int:id>/intro')
def intro(id):
    """
    Page d'introduction à l'application (guide d'utilisation)
    """
    return render_template('models/intro.html', id=id)


@bp.route('/<int:id>/data')
def data(id):
    """
    Page de gestion des données
    """
    model = get_model(id)
    if model is None:
        return redirect(url_for('models.index'))

    # vérifier si le dossier 'importer/<id>' existe
    for path in ['importer/' + str(id), 'src/static/data/' + str(id)]:
        if not os.path.exists(path):
            os.makedirs(path)

    return render_template('models/editor/data.html', id=id, model=model, page='data')


@bp.route('/<int:id>/etiquetage')
def etiquetage(id):
    """
    Etiquetage des données
    """
    model = get_model(id)
    if model is None:
        return redirect(url_for('models.index'))
    return render_template('models/editor/etiquetage.html', id=id, model=model, page='etiquetage')


@bp.route('/<int:id>/entrainement')
def entrainement(id):
    """
    Entrainement du modèle
    """
    model = get_model(id)
    if model is None:
        return redirect(url_for('models.index'))
    return render_template('models/editor/train.html', id=id, model=model, page='train')


@bp.route('/<int:id>/prediction')
def prediction(id):
    """
    Faire des prédictions à partir d'un modèle entrainé
    """
    model = get_model(id)
    if model is None:
        return redirect(url_for('models.index'))

    # récupérer tous les fichiers .pth dans le dossier 'output/<id>'
    path = 'output/' + str(id)
    if os.path.exists(path):

        files = [(f, os.path.getctime(os.path.join(path, f)))
                 for f in os.listdir(path) if f.endswith('.pth')]

        # trier les fichiers par date de création
        files.sort(key=lambda x: x[1], reverse=True)
        return render_template('models/editor/prediction.html', id=id, model=model, page='prediction', files=files, inexistant=False)

    else:
        return render_template('models/editor/prediction.html', id=id, model=model, page='prediction', files=[], inexistant=True)


@bp.route('/<int:id>/prediction/<string:file>')
def prediction_model(id, file):
    """
    Charge le modèle demandé
    """
    model = get_model(id)
    if model is None:
        return redirect(url_for('models.index'))

    return render_template('models/editor/prediction.html', id=id, model=model, page='prediction', files=[], inexistant=False, file=file)
