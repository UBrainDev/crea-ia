# displays a list of all the available models in the database (path: /models)

from flask import Blueprint, render_template, request, redirect, url_for
from src.db import get_db

bp = Blueprint('models', __name__, url_prefix='/models')


@bp.route('/')
def index():
    db = get_db()
    models = db.execute('SELECT * FROM models').fetchall()

    # si aucun modèle n'est repertorié
    if len(models) == 1:
        return render_template('models/intro.html')
    return render_template('models/index.html', models=models)


@bp.route('/create', methods=('GET', 'POST'))
def create():
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


@bp.route('/<int:id>/edit')
def edit(id):
    db = get_db()
    model = db.execute('SELECT * FROM models WHERE id = ?', (id,)).fetchone()

    # si le modèle demandé n'existe pas, on redirige vers la page d'accueil
    if model is None:
        return redirect(url_for('models.index'))

    return render_template('models/edit.html', model=model)
