import os
from flask import Flask

def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        instance_relative_config=True
    )
    app.config.from_mapping(SECRET_KEY='dev')

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
