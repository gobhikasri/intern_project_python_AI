import os
import sqlite3
import pandas as pd

def clean_data():
    raw_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'raw', 'weather_data.csv')
    processed_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'processed', 'cleaned_weather.csv')

    print(f"Loading raw weather data from {raw_path}...")
    df = pd.read_csv(raw_path)

    # Basic data cleaning
    df.dropna(subset=['Year', 'PeriodNum', 'Value'], inplace=True)
    df['Year'] = df['Year'].astype(int)
    df['MonthNum'] = df['MonthNum'].astype(int)
    df['Value'] = df['Value'].astype(float)
    df['PeriodNum'] = df['PeriodNum'].astype(str)

    # Sort sequentially
    df = df.sort_values(by=['Year', 'MonthNum']).reset_index(drop=True)

    # Ensure processed folder exists
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"Cleaned data saved to {processed_path}. Shape: {df.shape}")
    return df

def seed_database(df):
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'ninosense.db')

    print(f"Seeding database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month_txt TEXT,
            month_num INTEGER,
            period_txt TEXT,
            period_num TEXT,
            value REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            threshold REAL NOT NULL,
            direction TEXT NOT NULL, -- 'above' or 'below'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS triggered_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alert_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            value REAL NOT NULL,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
        )
    ''')

    # Seed weather_data table
    cursor.execute('DELETE FROM weather_data') # Clear existing to prevent duplicate seeding
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO weather_data (year, month_txt, month_num, period_txt, period_num, value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            int(row['Year']),
            str(row['MonthTxt']),
            int(row['MonthNum']),
            str(row['PeriodTxt']),
            str(row['PeriodNum']),
            float(row['Value'])
        ))

    conn.commit()
    print(f"Successfully seeded {len(df)} records into the weather_data table.")
    conn.close()

if __name__ == '__main__':
    df = clean_data()
    seed_database(df)
