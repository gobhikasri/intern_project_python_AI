from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.database.models import (
    create_alert, get_alerts_by_user, delete_alert, get_triggered_alerts_by_user, mark_triggered_alerts_as_read
)
from backend.services.alert_service import check_and_trigger_alerts

alert_bp = Blueprint('alert', __name__, template_folder='../../frontend/templates')

@alert_bp.route('/alerts')
@login_required
def alerts_view():
    # Pass user triggered alerts directly into templates for initial render
    notifications = get_triggered_alerts_by_user(current_user.id)
    unread_count = sum(1 for n in notifications if not n['is_read'])
    
    return render_template(
        'alerts.html',
        notifications=notifications,
        unread_count=unread_count
    )

@alert_bp.route('/api/alerts', methods=['GET', 'POST'])
@login_required
def alerts_api():
    if request.method == 'GET':
        alerts = [dict(r) for r in get_alerts_by_user(current_user.id)]
        return jsonify(alerts)
        
    if request.method == 'POST':
        # API request or standard form request
        if request.is_json:
            data = request.json
        else:
            data = request.form
            
        try:
            threshold = float(data.get('threshold'))
            direction = str(data.get('direction')).lower()
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid threshold. Must be a decimal number.'}), 400
            
        if direction not in ['above', 'below']:
            return jsonify({'error': "Invalid direction. Must be 'above' or 'below'."}), 400
            
        create_alert(current_user.id, threshold, direction)
        
        # Trigger an immediate check so that if the current status matches, it triggers immediately!
        check_and_trigger_alerts()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Alert threshold created successfully.'})
        else:
            flash('Alert threshold created successfully.', 'success')
            return redirect(url_for('alert.alerts_view'))

@alert_bp.route('/api/alerts/delete/<int:alert_id>', methods=['POST', 'DELETE'])
@login_required
def delete_alert_api(alert_id):
    success = delete_alert(alert_id, current_user.id)
    if success:
        message = 'Alert threshold deleted.'
        status_code = 200
    else:
        message = 'Alert not found or unauthorized.'
        status_code = 404
        
    if request.method == 'POST' and not request.is_json:
        flash(message, 'info' if success else 'danger')
        return redirect(url_for('alert.alerts_view'))
        
    return jsonify({'success': success, 'message': message}), status_code

# Get triggered alerts API
@alert_bp.route('/api/alerts/triggered', methods=['GET'])
@login_required
def triggered_alerts_api():
    triggered = [dict(r) for r in get_triggered_alerts_by_user(current_user.id)]
    return jsonify(triggered)

@alert_bp.route('/api/alerts/triggered/read', methods=['POST'])
@login_required
def mark_read_api():
    mark_triggered_alerts_as_read(current_user.id)
    return jsonify({'success': True})

@alert_bp.route('/api/alerts/test-trigger', methods=['POST'])
@login_required
def test_trigger_api():
    """
    Simulates a backend data ingestion cycle, re-checking active alerts.
    """
    triggered_count = check_and_trigger_alerts()
    return jsonify({
        'success': True, 
        'triggered_alerts_count': triggered_count,
        'message': f"Evaluated rules. Triggered {triggered_count} alerts."
    })
