import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_assets import Bundle, Environment

db = SQLAlchemy()
migrate = Migrate()

bundles = {
        'd3_viz':Bundle('home.js', 'map.js', 'foresight.js',
                        output='gen/main.js'),

        'home_css':Bundle('home.css',
                          output='gen/main.css'),
}

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key',
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        UPLOAD_FOLDER = UPLOAD_FOLDER
    )

    db.init_app(app)
    migrate.init_app(app, db)

    assets = Environment(app)
    assets.register(bundles)

    from . import models
    from . import routes

    app.register_blueprint(routes.bp)

    return app
