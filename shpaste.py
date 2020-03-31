# Copyright 2020 hellodoge
# Licensed under the Apache License, Version 2.0

from flask import Flask
from flask import render_template, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
from random import getrandbits

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)


class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.Integer, nullable=False)
    private = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text)

    def get_public(self):
        return self.public

    def get_private(self):
        return self.private


# noinspection PyUnboundLocalVariable
def get_entity(link, func):
    try:
        entity_id = int(link[:-8], 16)
        sign = int(link[-8:], 16)
    except ValueError:
        abort(404)
    entity = Entity.query.get_or_404(entity_id)
    if sign != func(entity):
        abort(404)
    return entity


def wrap(entity_id, link):
    link = hex(link)[2:]
    return hex(entity_id)[2:] + '0'*(8-len(link)) + link


@app.route('/')
def index():
    return render_template('index.html', url=Configuration.SITE_URL)


@app.route('/create')
def create():
    public = getrandbits(31)
    private = getrandbits(31)
    entity = Entity(public=public, private=private)
    db.session.add(entity)
    db.session.commit()
    return jsonify(
        {'Public link': f'{Configuration.SITE_URL}/{wrap(entity.id, public)}',
         'Private link': f'{Configuration.SITE_URL}/{wrap(entity.id, private)}'}
    )


@app.route('/<entity_public>')
def fetch(entity_public):
    entity = get_entity(entity_public, Entity.get_public)
    return str(entity.text)


@app.route('/<entity_private>/<text>')
def update(entity_private, text):
    entity = get_entity(entity_private, Entity.get_private)
    entity.text = text
    db.session.commit()
    return jsonify(
        {'Public link': f'{Configuration.SITE_URL}/{wrap(entity.id, entity.public)}'}
    )


if __name__ == '__main__':
    app.run()
