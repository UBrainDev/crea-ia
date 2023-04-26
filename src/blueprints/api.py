from flask import Blueprint, render_template, request, redirect, url_for
from src.db import get_db
import os
import sys
import subprocess

bp = Blueprint('api', __name__, url_prefix='/api')

# Extensions de fichiers autorisées pour chaque type de modèle
MODEL_TYPES = {
    1: ['png', 'jpg', 'jpeg'],
    2: ['png', 'jpg', 'jpeg'],
    3: ['txt']
}


@bp.route('/models/<int:id>/data')
def get_model_data(id):
    """
    Récupère le jeu de données d'un modèle sous forme de JSON
    """
    db = get_db()
    model = db.execute(
        'SELECT type FROM models WHERE id = ?', (id,)).fetchone()
    if model is None:
        return {'error': 'Modèle inexistant'}, 404

    # vérifier si il y a des fichiers dans le dossier 'importer/<id>'
    imported_files = os.listdir('importer/' + str(id))
    incorrect_files = []

    if len(imported_files) > 0:
        for file in imported_files:

            # vérifier que l'extension du fichier est valide
            ext = file.split('.')[-1]
            if ext not in MODEL_TYPES[model['type']]:
                incorrect_files.append(file)
                continue

            # ajouter l'entrée dans la base de données
            l = db.execute(
                'INSERT INTO data_elements (model_id, ext) VALUES (?, ?)', (id, ext))

            # déplacer le fichier dans le dossier 'src/static/data/<id>'
            os.rename('importer/' + str(id) + '/' + file,
                      'src/static/data/' + str(id) + '/' + str(l.lastrowid) + '.' + ext)

    # enregistrer les changements
    db.commit()

    data = db.execute(
        'SELECT * FROM data_elements WHERE model_id = ?', (id,)).fetchall()
    return {'data': [[row['id'], row['ext']] for row in data], 'incorrect': incorrect_files}, 200


@bp.route('/models/<int:id>/openImportFolder')
def open_import_folder(id):
    """
    Ouvre le dossier d'importation du modèle
    """
    if sys.platform == 'win32':
        os.startfile(os.getcwd() + '/importer/' + str(id))
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, os.getcwd() + '/importer/' + str(id)])
    return {}, 200


def get_next_data_element(model_id):
    """
    Récupère et renvoie les données du prochain élément à étiqueter
    """
    db = get_db()
    data = db.execute(
        'SELECT * FROM data_elements WHERE model_id = ? AND tags IS NULL', (model_id,)).fetchone()
    if data is None:
        return {'code': 1}, 200
    return {'code': 0, 'data': {'id': data['id'], 'ext': data['ext']}}, 200


@bp.route('/models/<int:id>/labelling', methods=['GET', 'POST'])
def get_labelling_data(id):
    """
    Récupère les données d'étiquetage du modèle (étiquettes, document, etc.)
    Ou enregistrer de nouvelles étiquettes
    """
    db = get_db()
    model = db.execute(
        'SELECT type FROM models WHERE id = ?', (id,)).fetchone()
    if model is None:
        return {'error': 'Modèle inexistant'}, 404

    if request.method == 'GET':
        # récupérer les étiquettes
        data = db.execute(
            'SELECT * FROM labels WHERE model_id = ?', (id,)).fetchall()
        next_data = get_next_data_element(id)
        return {'labels': [row['name'] for row in data], 'next_data': next_data[0]}, 200

    else:
        # enregistrer les nouvelles étiquettes
        labels = request.get_json()['labels']
        label_ids = []
        for label in labels:
            cursor = db.execute(
                'INSERT INTO labels (model_id, name) VALUES (?, ?)', (id, label))
            label_ids.append(cursor.lastrowid)
        db.commit()
        return {'label_ids': label_ids}, 200


@bp.route('/models/<int:id>/data/<int:data_id>', methods=['GET', 'DELETE'])
def get_data_element(id, data_id):
    """
    Récupère ou supprime un élément du jeu de données d'un modèle
    """
    if request.method == 'DELETE':
        db = get_db()
        data = db.execute(
            'SELECT * FROM data_elements WHERE id = ?', (data_id,)).fetchone()
        if data is None:
            return {'error': 'Elément inexistant'}, 404
        if data['model_id'] != id:
            return {'error': 'Le modèle ne correspond pas'}, 400

        # supprimer l'entrée dans la base de données
        db.execute('DELETE FROM data_elements WHERE id = ?', (data_id,))

        # supprimer le fichier dans le dossier 'src/static/data/<id>'
        os.remove('src/static/data/' + str(id) + '/' +
                  str(data_id) + '.' + data['ext'])

        # enregistrer les changements
        db.commit()
        return {}, 200


@bp.route('/models/<int:id>/data/<int:data_id>/labels', methods=['GET', 'POST'])
def get_data_element_labels(id, data_id):
    """
    Récupère ou enregistre les étiquettes d'un élément du jeu de données d'un modèle
    """
    db = get_db()
    data = db.execute(
        'SELECT * FROM data_elements WHERE id = ?', (data_id,)).fetchone()
    if data is None:
        return {'error': 'Elément inexistant'}, 404
    if data['model_id'] != id:
        return {'error': 'Le modèle ne correspond pas'}, 400

    if request.method == 'GET':
        # récupérer les étiquettes
        return {'labels': data['tags']}, 200

    else:
        # mettre à jour les étiquettes de l'élément
        labels = ','.join(request.get_json()['labels'])
        db.execute(
            'UPDATE data_elements SET tags = ? WHERE id = ?', (labels, data_id))
        db.commit()
        next_data = get_next_data_element(id)
        return {'next_data': next_data[0]}, 200
