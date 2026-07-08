import os
import json
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from backend.services.prediction_service import generate_forecast

prediction_bp = Blueprint('prediction', __name__, template_folder='../../frontend/templates')

@prediction_bp.route('/prediction')
@login_required
def prediction_view():
    return render_template('prediction.html')

@prediction_bp.route('/api/prediction/forecast')
@login_required
def forecast_api():
    """
    Returns the 6-month ML forecast.
    Accepts an optional 'custom_oni' query parameter to run interactive simulation models.
    """
    custom_oni = request.args.get('custom_oni', None)
    if custom_oni is not None:
        try:
            custom_oni = float(custom_oni)
        except ValueError:
            return jsonify({'error': 'Invalid custom_oni value. Must be a decimal number.'}), 400
            
    forecast = generate_forecast(custom_current_oni=custom_oni)
    return jsonify(forecast)

@prediction_bp.route('/api/prediction/metadata')
@login_required
def metadata_api():
    """
    Reads the model_metadata.json file generated during model training and returns it.
    """
    metadata_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model_metadata.json')
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'Model metadata not found. Run model training first.'}), 404
        
    with open(metadata_path, 'r') as f:
        data = json.load(f)
        
    return jsonify(data)
