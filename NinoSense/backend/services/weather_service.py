import numpy as np
from backend.database.models import get_latest_weather, get_weather_all, get_weather_range

def get_oni_phase(value):
    """
    Returns the climate phase (El Nino, La Nina, Neutral) and intensity based on ONI.
    """
    if value >= 0.5:
        phase = "El Niño"
        if value >= 2.0:
            intensity = "Very Strong"
        elif value >= 1.5:
            intensity = "Strong"
        elif value >= 1.0:
            intensity = "Moderate"
        else:
            intensity = "Weak"
    elif value <= -0.5:
        phase = "La Niña"
        if value <= -2.0:
            intensity = "Very Strong"
        elif value <= -1.5:
            intensity = "Strong"
        elif value <= -1.0:
            intensity = "Moderate"
        else:
            intensity = "Weak"
    else:
        phase = "Neutral"
        intensity = "N/A"
        
    return phase, intensity

def get_current_status():
    """
    Fetches the latest database record and computes its status.
    """
    latest = get_latest_weather()
    if not latest:
        return None
        
    phase, intensity = get_oni_phase(latest['value'])
    
    return {
        'year': latest['year'],
        'month_txt': latest['month_txt'],
        'period_txt': latest['period_txt'],
        'period_num': latest['period_num'],
        'value': latest['value'],
        'phase': phase,
        'intensity': intensity
    }

def get_dashboard_statistics():
    """
    Generates statistics for cards and chart plots on the main dashboard.
    """
    all_data = get_weather_all()
    if not all_data:
        return {}
        
    values = [r['value'] for r in all_data]
    
    # Calculate stats
    latest = get_current_status()
    total_records = len(values)
    mean_val = float(np.mean(values))
    max_val = float(np.max(values))
    min_val = float(np.min(values))
    
    # Count occurrences
    el_nino_count = sum(1 for v in values if v >= 0.5)
    la_nina_count = sum(1 for v in values if v <= -0.5)
    neutral_count = total_records - el_nino_count - la_nina_count
    
    # Prepares charts: last 36 periods
    chart_len = min(36, total_records)
    recent_records = all_data[-chart_len:]
    
    chart_labels = [r['period_txt'] for r in recent_records]
    chart_values = [r['value'] for r in recent_records]
    
    return {
        'latest': latest,
        'summary': {
            'total_records': total_records,
            'mean': round(mean_val, 2),
            'max': round(max_val, 2),
            'min': round(min_val, 2),
            'el_nino_percent': round((el_nino_count / total_records) * 100, 1),
            'la_nina_percent': round((la_nina_count / total_records) * 100, 1),
            'neutral_percent': round((neutral_count / total_records) * 100, 1),
        },
        'chart': {
            'labels': chart_labels,
            'values': chart_values
        }
    }
