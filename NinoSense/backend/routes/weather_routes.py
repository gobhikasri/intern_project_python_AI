from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from backend.services.weather_service import get_current_status, get_dashboard_statistics

weather_bp = Blueprint('weather', __name__, template_folder='../../frontend/templates')

@weather_bp.route('/')
def index_view():
    latest_status = get_current_status()
    # Renders the landing portal homepage (publicly accessible)
    return render_template('index.html', status=latest_status)

@weather_bp.route('/dashboard')
@login_required
def dashboard_view():
    latest_status = get_current_status()
    # Renders the dashboard shell (authenticated only)
    return render_template('dashboard.html', status=latest_status)

@weather_bp.route('/api/weather/dashboard')
@login_required
def dashboard_api():
    """
    Returns statistics and chart series data for the dashboard in JSON format.
    """
    stats = get_dashboard_statistics()
    return jsonify(stats)
