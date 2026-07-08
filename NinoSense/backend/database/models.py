import sqlite3
from backend.database.database import get_db_connection

# ==========================================
# User Models
# ==========================================

def create_user(email, name, password_hash=None, google_id=None, profile_pic=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (email, name, password_hash, google_id, profile_pic)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, name, password_hash, google_id, profile_pic))
        conn.commit()
        user_id = cursor.lastrowid
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_google_id(google_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE google_id = ?', (google_id,)).fetchone()
    conn.close()
    return user

# ==========================================
# Weather Data Models
# ==========================================

def get_latest_weather():
    conn = get_db_connection()
    # Sort by year desc and month_num desc
    row = conn.execute('SELECT * FROM weather_data ORDER BY year DESC, month_num DESC LIMIT 1').fetchone()
    conn.close()
    return row

def get_weather_all():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM weather_data ORDER BY year ASC, month_num ASC').fetchall()
    conn.close()
    return rows

def get_weather_range(start_year, end_year):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT * FROM weather_data 
        WHERE year >= ? AND year <= ? 
        ORDER BY year ASC, month_num ASC
    ''', (start_year, end_year)).fetchall()
    conn.close()
    return rows

def _build_filter_clause(year_filter, phase_filter):
    clauses = []
    params = []
    
    if year_filter:
        clauses.append("year = ?")
        params.append(int(year_filter))
        
    if phase_filter:
        if phase_filter == 'el_nino':
            clauses.append("value >= 0.5")
        elif phase_filter == 'la_nina':
            clauses.append("value <= -0.5")
        elif phase_filter == 'neutral':
            clauses.append("value > -0.5 AND value < 0.5")
            
    clause_str = " WHERE " + " AND ".join(clauses) if clauses else ""
    return clause_str, params

def get_weather_paginated(limit, offset, year_filter=None, phase_filter=None):
    conn = get_db_connection()
    clause_str, params = _build_filter_clause(year_filter, phase_filter)
    
    query = f'''
        SELECT * FROM weather_data 
        {clause_str} 
        ORDER BY year DESC, month_num DESC 
        LIMIT ? OFFSET ?
    '''
    rows = conn.execute(query, params + [limit, offset]).fetchall()
    conn.close()
    return rows

def count_weather_records(year_filter=None, phase_filter=None):
    conn = get_db_connection()
    clause_str, params = _build_filter_clause(year_filter, phase_filter)
    
    query = f'SELECT COUNT(*) FROM weather_data {clause_str}'
    count = conn.execute(query, params).fetchone()[0]
    conn.close()
    return count

# ==========================================
# Alert Config & Notifications
# ==========================================

def create_alert(user_id, threshold, direction):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (user_id, threshold, direction)
        VALUES (?, ?, ?)
    ''', (user_id, threshold, direction))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_alerts_by_user(user_id):
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM alerts WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return rows

def delete_alert(alert_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alerts WHERE id = ? AND user_id = ?', (alert_id, user_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def get_all_active_alerts():
    conn = get_db_connection()
    # Join with users to know who to notify
    rows = conn.execute('''
        SELECT a.id as alert_id, a.user_id, a.threshold, a.direction, u.email, u.name 
        FROM alerts a
        JOIN users u ON a.user_id = u.id
    ''').fetchall()
    conn.close()
    return rows

def create_triggered_alert(user_id, alert_id, period, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO triggered_alerts (user_id, alert_id, period, value)
        VALUES (?, ?, ?, ?)
    ''', (user_id, alert_id, period, value))
    conn.commit()
    triggered_id = cursor.lastrowid
    conn.close()
    return triggered_id

def get_triggered_alerts_by_user(user_id):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT ta.id, ta.period, ta.value, ta.triggered_at, ta.is_read, a.threshold, a.direction
        FROM triggered_alerts ta
        JOIN alerts a ON ta.alert_id = a.id
        WHERE ta.user_id = ?
        ORDER BY ta.triggered_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return rows

def mark_triggered_alerts_as_read(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE triggered_alerts SET is_read = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
