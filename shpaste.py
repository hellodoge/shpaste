from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
from random import getrandbits

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)


class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.Integer, unique=True, nullable=False)
    private = db.Column(db.Integer, unique=True, nullable=False)
    text = db.Column(db.Text)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entity': Entity}


@app.route('/')
def index():
    return render_template('index.html', url=Configuration.SITE_URL)


@app.route('/create')
def create():
    while True:
        public = getrandbits(32)
        private = getrandbits(32)
        public_check = Entity.query.filter_by(public=public).first()
        private_check = Entity.query.filter_by(public=public).first()
        if public_check or private_check:
            continue
        break
    entity = Entity(public=public, private=private)
    db.session.add(entity)
    db.session.commit()
    return f'Public link {Configuration.SITE_URL}/{hex(public)[2:]}\n' + \
           f'Private link {Configuration.SITE_URL}/{hex(private)[2:]}\n'


@app.route('/<entity_public>')
def view(entity_public):
    try:
        entity_public = int(entity_public, 16)
    except ValueError:
        return 'Public link is invalid\n'
    entity = Entity.query.filter_by(public=entity_public).first_or_404()
    return str(entity.text)


@app.route('/<entity_private>/<text>')
def change(entity_private, text):
    try:
        entity_private = int(entity_private, 16)
    except ValueError:
        return 'Private link is invalid\n'
    entity = Entity.query.filter_by(private=entity_private).first_or_404()
    entity.text = text
    db.session.commit()
    return f'Public link {Configuration.SITE_URL}/{hex(entity.public)[2:]}\n'


if __name__ == '__main__':
    app.run()
