from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response, jsonify, abort
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import time 

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

bp = Blueprint('scc', __name__)

@bp.route('/')
def index():
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        db = get_db()
        condition = db.execute(
        'SELECT condition'
        ' FROM scc WHERE username = ?', (g.user['username'], )
        ).fetchone()
        return render_template('scc/index.html', condition=condition)


@bp.route('/set/<string:condition>')
def set(condition):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        db = get_db()
        db.execute(
            'UPDATE scc'
            ' SET condition = ? WHERE username = ?',
            (condition, g.user['username'])
        )
        db.commit()
        return redirect(url_for('index'))
    
    
@bp.route('/view/<string:username>')
def view(username):
    db = get_db()
    condition = db.execute(
        'SELECT condition'
        ' FROM scc WHERE username = ?', (username, )
    ).fetchone()
    if condition[0] == "404":
        resp = render_template('scc/' + condition[0] + '.html', condition=condition)
        return (resp, 404)
    elif condition[0] == "500":
        resp = render_template('scc/' + condition[0] + '.html', condition=condition)
        return (resp, 500)
    elif condition[0] == "timeout":
        time.sleep(62)
        return render_template('scc/' + condition[0] + '.html', condition=condition)
    elif condition[0] == "cookies":
        resp = make_response(render_template('scc/' + condition[0] + '.html', condition=condition))
        resp.set_cookie('SplunkSynthetic', 'abc123')
        return resp
    else:
        return render_template('scc/' + condition[0] + '.html', condition=condition)


@bp.route('/lorem')
def lorem():
    return render_template('scc/lorem.html')


@bp.route('/api/v1/<string:username>/books/all', methods=['GET'])
def api_all(username):
    
    return jsonify(books)
    

@bp.route('/api/v1/<string:username>/books', methods=['GET'])
def api_id(username):
    # Check if an ID was provided as part of the URL.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    results = []

    for book in books:
        if book['id'] == id:
            results.append(book)

    if len(results) == 0:
        abort(404)
        
    return jsonify(results)


@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)