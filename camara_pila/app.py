from flask import Flask, jsonify

from routes import main_bp
from stack import PhotoStack


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.extensions["photo_stack"] = PhotoStack(capacity=30)

    app.register_blueprint(main_bp)

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify(error="La captura supera el límite de 5 MiB."), 413

    return app


app = create_app()  