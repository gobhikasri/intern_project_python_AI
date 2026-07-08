import tempfile
import os
from flask import Blueprint, render_template, request, jsonify, send_file, make_response
from flask_login import login_required
import csv
from io import StringIO

from backend.database.models import (
    get_weather_paginated, count_weather_records, get_weather_all
)
from backend.services.weather_service import get_current_status, get_oni_phase
from backend.services.prediction_service import generate_forecast
from backend.reports.pdf_generator import generate_report_pdf

history_bp = Blueprint('history', __name__, template_folder='../../frontend/templates')

@history_bp.route('/history')
@login_required
def history_view():
    return render_template('history.html')

@history_bp.route('/api/history')
@login_required
def history_api():
    """
    Returns paginated weather logs with optional filtering.
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 15))
    except ValueError:
        return jsonify({'error': 'Page and limit must be integers.'}), 400
        
    year = request.args.get('year', None)
    phase = request.args.get('phase', None)
    
    # Clean filters
    if year == '': year = None
    if phase == '': phase = None
    
    offset = (page - 1) * limit
    
    records = get_weather_paginated(limit, offset, year, phase)
    total_records = count_weather_records(year, phase)
    
    # Format database rows to serializable dict list
    serializable_records = []
    for r in records:
        r_dict = dict(r)
        phase_name, intensity = get_oni_phase(r_dict['value'])
        r_dict['phase'] = phase_name
        r_dict['intensity'] = intensity
        serializable_records.append(r_dict)
        
    total_pages = (total_records + limit - 1) // limit
    
    return jsonify({
        'records': serializable_records,
        'total': total_records,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    })

@history_bp.route('/history/export/csv')
@login_required
def export_csv():
    """
    Exports the complete historical weather index as a CSV spreadsheet.
    """
    year = request.args.get('year', None)
    phase = request.args.get('phase', None)
    if year == '': year = None
    if phase == '': phase = None

    # Fetch matching records (paginate query with limit = count)
    total = count_weather_records(year, phase)
    records = get_weather_paginated(total, 0, year, phase)
    
    # Write CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Year', 'MonthTxt', 'MonthNum', 'PeriodTxt', 'PeriodNum', 'Value', 'Phase', 'Intensity'])
    
    for r in records:
        phase_name, intensity = get_oni_phase(r['value'])
        cw.writerow([
            r['year'], r['month_txt'], r['month_num'], 
            r['period_txt'], r['period_num'], r['value'], 
            phase_name, intensity
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=ninosense_weather_history.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@history_bp.route('/history/export/pdf')
@login_required
def export_pdf():
    """
    Generates and downloads the meteorological advisory summary report in PDF format.
    """
    current_status = get_current_status()
    forecast = generate_forecast()
    
    # Create temp file
    temp_dir = tempfile.gettempdir()
    temp_pdf_path = os.path.join(temp_dir, 'ninosense_briefing.pdf')
    
    try:
        generate_report_pdf(temp_pdf_path, current_status, forecast)
        
        response = send_file(
            temp_pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='NinoSense_Climate_Bulletin.pdf'
        )
        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': f"Failed to generate PDF: {e}"}), 500
