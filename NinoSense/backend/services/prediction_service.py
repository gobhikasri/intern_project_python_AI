import os
import pickle
import numpy as np
import pandas as pd
from backend.database.models import get_weather_all
from backend.services.weather_service import get_oni_phase

_MODEL = None

def load_model():
    global _MODEL
    if _MODEL is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'heat_model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                _MODEL = pickle.load(f)
        else:
            print(f"Warning: Model not found at {model_path}")
    return _MODEL

# Seasons rolling mapping
SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]

def get_next_period(year, month_num):
    """
    Computes the next month_num, year, and season name.
    """
    month_num += 1
    if month_num > 12:
        month_num = 1
        year += 1
    season_name = SEASONS[month_num - 1]
    return year, month_num, season_name

def generate_forecast(custom_current_oni=None):
    """
    Builds the feature vector from the latest DB records and predicts the next 6 months of ONI.
    Supports injecting a custom current ONI for simulation studies.
    """
    model = load_model()
    if not model:
        return []

    # Get recent records (need at least 12 records to build lag_11)
    all_records = get_weather_all()
    if len(all_records) < 12:
        return []

    # Format into dataframe to easily compute features
    df = pd.DataFrame([{
        'Year': r['year'],
        'MonthNum': r['month_num'],
        'Value': r['value']
    } for r in all_records])

    # Sort sequentially
    df = df.sort_values(by=['Year', 'MonthNum']).reset_index(drop=True)

    if custom_current_oni is not None:
        # Override the latest value for simulation
        df.loc[df.index[-1], 'Value'] = float(custom_current_oni)

    # Extract required lag features relative to index t (which is the last row)
    t = len(df) - 1
    
    year = int(df.loc[t, 'Year'])
    month_num = int(df.loc[t, 'MonthNum'])
    oni_current = float(df.loc[t, 'Value'])
    
    oni_lag_1 = float(df.loc[t-1, 'Value'])
    oni_lag_2 = float(df.loc[t-2, 'Value'])
    oni_lag_3 = float(df.loc[t-3, 'Value'])
    oni_lag_4 = float(df.loc[t-4, 'Value'])
    oni_lag_5 = float(df.loc[t-5, 'Value'])
    oni_lag_11 = float(df.loc[t-11, 'Value'])
    
    # Rolling averages using [t, t-1, t-2] and [t ... t-5]
    vals_3 = df.loc[t-2:t, 'Value'].tolist()
    vals_6 = df.loc[t-5:t, 'Value'].tolist()
    
    oni_roll_mean_3 = float(np.mean(vals_3))
    oni_roll_mean_6 = float(np.mean(vals_6))
    oni_roll_std_3 = float(np.std(vals_3))

    # Construct feature list (matches training column order)
    feature_dict = {
        'year': [year],
        'month_num': [month_num],
        'oni_current': [oni_current],
        'oni_lag_1': [oni_lag_1],
        'oni_lag_2': [oni_lag_2],
        'oni_lag_3': [oni_lag_3],
        'oni_lag_4': [oni_lag_4],
        'oni_lag_5': [oni_lag_5],
        'oni_lag_11': [oni_lag_11],
        'oni_roll_mean_3': [oni_roll_mean_3],
        'oni_roll_mean_6': [oni_roll_mean_6],
        'oni_roll_std_3': [oni_roll_std_3]
    }
    
    X_pred = pd.DataFrame(feature_dict)
    
    # Execute prediction: returns array of shape (1, 6)
    Y_pred = model.predict(X_pred)[0]

    # Generate dates and construct predictions list
    forecast = []
    curr_yr, curr_mon = year, month_num
    
    # Calculate confidence bands: standard error grows over time
    # Let's say baseline confidence margin is ±0.1°C + 0.08°C per step
    for i, predicted_val in enumerate(Y_pred):
        curr_yr, curr_mon, curr_season = get_next_period(curr_yr, curr_mon)
        period_txt = f"{curr_yr}-{curr_season}"
        period_num = f"{curr_yr}-{curr_mon:02d}"
        
        phase, intensity = get_oni_phase(predicted_val)
        
        margin = 0.10 + (i * 0.08)
        
        forecast.append({
            'step': i + 1,
            'period_txt': period_txt,
            'period_num': period_num,
            'value': round(float(predicted_val), 3),
            'value_upper': round(float(predicted_val + margin), 3),
            'value_lower': round(float(predicted_val - margin), 3),
            'phase': phase,
            'intensity': intensity
        })
        
    return forecast
