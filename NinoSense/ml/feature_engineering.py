import pandas as pd
import numpy as np

def create_features_and_targets(df, forecast_horizon=6):
    """
    Constructs lag features and future targets for multi-step forecasting.
    Features: Lags of ONI (t, t-1, t-2, t-3, t-4, t-5, t-11) and rolling stats.
    Targets: Future values (t+1, t+2, t+3, t+4, t+5, t+6)
    """
    df = df.copy().sort_values(by=['Year', 'MonthNum']).reset_index(drop=True)
    
    # Feature dictionary
    features = pd.DataFrame(index=df.index)
    features['year'] = df['Year']
    features['month_num'] = df['MonthNum']
    features['oni_current'] = df['Value'] # Value at t
    
    # Create lags relative to t
    features['oni_lag_1'] = df['Value'].shift(1)   # t-1
    features['oni_lag_2'] = df['Value'].shift(2)   # t-2
    features['oni_lag_3'] = df['Value'].shift(3)   # t-3
    features['oni_lag_4'] = df['Value'].shift(4)   # t-4
    features['oni_lag_5'] = df['Value'].shift(5)   # t-5
    features['oni_lag_11'] = df['Value'].shift(11) # t-11 (same month last year)
    
    # Rolling averages relative to t (using current and past values)
    features['oni_roll_mean_3'] = df['Value'].rolling(window=3).mean()
    features['oni_roll_mean_6'] = df['Value'].rolling(window=6).mean()
    features['oni_roll_std_3'] = df['Value'].rolling(window=3).std()
    
    # Create targets: value at t+1, t+2, ..., t+forecast_horizon
    targets = pd.DataFrame(index=df.index)
    for h in range(1, forecast_horizon + 1):
        targets[f'target_tplus_{h}'] = df['Value'].shift(-h)
        
    # Combine and drop rows that have NaNs (ends/starts of time series)
    combined = pd.concat([features, targets], axis=1)
    combined.dropna(inplace=True)
    
    # Separate features and targets
    feature_cols = [
        'year', 'month_num', 'oni_current', 
        'oni_lag_1', 'oni_lag_2', 'oni_lag_3', 'oni_lag_4', 'oni_lag_5', 'oni_lag_11',
        'oni_roll_mean_3', 'oni_roll_mean_6', 'oni_roll_std_3'
    ]
    target_cols = [f'target_tplus_{h}' for h in range(1, forecast_horizon + 1)]
    
    X = combined[feature_cols]
    Y = combined[target_cols]
    periods = df.loc[combined.index, 'PeriodNum']
    
    return X, Y, periods
