"""
Fix: add csrf_token_input helper and urlencode filter to Jinja2 env.
Update app/__init__.py to register these.
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .models import db, User
from config import Config
from markupsafe import Markup


login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="static")
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Jinja helpers
    from flask_wtf.csrf import generate_csrf

    @app.template_global()
    def csrf_token_input():
        return Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')

    @app.template_filter("urlencode")
    def urlencode_filter(s):
        from urllib.parse import quote_plus
        return quote_plus(str(s))

    # Register blueprints
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .trips.routes import trips_bp
    from .search.routes import search_bp
    from .profile.routes import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app
