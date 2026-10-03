from flask import Flask, redirect, url_for
from config import Config
from database import database
from routes import auth, dashboard, credentials
from security.authentication import load_logged_in_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Database
    database.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(credentials.bp)

    @app.before_request
    def before_request():
        load_logged_in_user()

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
