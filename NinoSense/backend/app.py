import os
from flask import Flask
from flask_login import LoginManager, current_user

from backend.config import Config
from backend.database.database import init_db
from backend.database.models import get_triggered_alerts_by_user
from backend.auth.user_model import User

# Import Blueprints
from backend.auth.auth_routes import auth_bp
from backend.routes.weather_routes import weather_bp
from backend.routes.prediction_routes import prediction_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.history_routes import history_bp

def create_app():
    # Set template and static folders relative to the frontend directory
    app = Flask(
        __name__,
        static_folder='../frontend/static',
        template_folder='../frontend/templates'
    )
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize DB tables
    init_db()
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(int(user_id))
        
    # Inject global unread notifications count into all templates
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            try:
                notifications = get_triggered_alerts_by_user(current_user.id)
                unread_count = sum(1 for n in notifications if not n['is_read'])
                return {'unread_notifications_count': unread_count}
            except Exception:
                return {'unread_notifications_count': 0}
        return {'unread_notifications_count': 0}
        
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(history_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Run locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
