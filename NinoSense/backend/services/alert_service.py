import os
import sqlite3
from datetime import datetime
from backend.database.database import get_db_connection
from backend.database.models import (
    get_latest_weather, get_all_active_alerts, create_triggered_alert
)

def check_and_trigger_alerts():
    """
    Compares the latest weather ONI reading with user-defined alert thresholds.
    Triggers database alerts and writes notification dispatches to a local log file.
    """
    latest = get_latest_weather()
    if not latest:
        return 0
        
    latest_val = latest['value']
    period = latest['period_txt']
    
    active_alerts = get_all_active_alerts()
    triggered_count = 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Establish log folder for mock notifications
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'notifications')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'notification_log.txt')
    
    for alert in active_alerts:
        user_id = alert['user_id']
        alert_id = alert['alert_id']
        threshold = alert['threshold']
        direction = alert['direction']
        user_email = alert['email']
        user_name = alert['name']
        
        # Check condition
        triggered = False
        if direction == 'above' and latest_val >= threshold:
            triggered = True
        elif direction == 'below' and latest_val <= threshold:
            triggered = True
            
        if triggered:
            # Check if already triggered for this user, alert, and period
            existing = conn.execute('''
                SELECT id FROM triggered_alerts 
                WHERE user_id = ? AND alert_id = ? AND period = ?
            ''', (user_id, alert_id, period)).fetchone()
            
            if not existing:
                # Write to database
                create_triggered_alert(user_id, alert_id, period, latest_val)
                triggered_count += 1
                
                # Write to simulated notification log
                log_message = (
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"NOTIFICATION DISPATCHED\n"
                    f"To: {user_name} ({user_email})\n"
                    f"Alert Rules: ONI {direction} threshold {threshold}°C\n"
                    f"Observed ONI: {latest_val}°C for period {period}\n"
                    f"Status: SENT (Simulated Email & SMS)\n"
                    f"--------------------------------------------------\n"
                )
                
                with open(log_path, 'a') as log_file:
                    log_file.write(log_message)
                    
    conn.close()
    return triggered_count
