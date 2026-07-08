import os
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from preprocess import clean_data
from feature_engineering import create_features_and_targets

def train_forecasting_model():
    processed_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'processed', 'cleaned_weather.csv')
    if not os.path.exists(processed_path):
        df = clean_data()
    else:
        df = pd.read_csv(processed_path)

    # 1. Create Features and Targets (6-month horizon)
    forecast_horizon = 6
    X, Y, periods = create_features_and_targets(df, forecast_horizon)

    # 2. Time-series Split: Train up to 2015, Test from 2016 onwards
    train_mask = X['year'] <= 2015
    X_train, Y_train = X[train_mask], Y[train_mask]
    X_test, Y_test = X[~train_mask], Y[~train_mask]
    test_periods = periods[~train_mask].tolist()

    print(f"Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    # 3. Fit Multi-Output Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, Y_train)

    # 4. Evaluate Predictions
    Y_pred_train = model.predict(X_train)
    Y_pred_test = model.predict(X_test)

    metrics = {}
    test_predictions_vs_actual = []

    # Calculate metrics for each step (1 to 6 months out)
    for i in range(forecast_horizon):
        step_name = f'tplus_{i+1}'
        
        train_mae = mean_absolute_error(Y_train.iloc[:, i], Y_pred_train[:, i])
        test_mae = mean_absolute_error(Y_test.iloc[:, i], Y_pred_test[:, i])
        
        train_rmse = np.sqrt(mean_squared_error(Y_train.iloc[:, i], Y_pred_train[:, i]))
        test_rmse = np.sqrt(mean_squared_error(Y_test.iloc[:, i], Y_pred_test[:, i]))
        
        train_r2 = r2_score(Y_train.iloc[:, i], Y_pred_train[:, i])
        test_r2 = r2_score(Y_test.iloc[:, i], Y_pred_test[:, i])
        
        metrics[step_name] = {
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'train_rmse': float(train_rmse),
            'test_rmse': float(test_rmse),
            'train_r2': float(train_r2),
            'test_r2': float(test_r2)
        }
        print(f"Step {step_name} - Test MAE: {test_mae:.4f}, Test R2: {test_r2:.4f}")

    # Prepare feature importances
    importances = model.feature_importances_
    feature_names = X.columns.tolist()
    feature_importance_dict = {name: float(imp) for name, imp in zip(feature_names, importances)}
    # Sort importances
    feature_importance_dict = dict(sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True))

    # Format sample test predictions vs actual for UI charts (limit to last 60 periods to avoid huge file)
    chart_len = min(60, len(test_periods))
    chart_periods = test_periods[-chart_len:]
    chart_actuals = Y_test.iloc[-chart_len:, 0].tolist() # t+1 actual
    chart_preds = Y_pred_test[-chart_len:, 0].tolist()   # t+1 predicted

    # Save trained model
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'heat_model.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

    # Save metadata JSON
    metadata = {
        'metrics': metrics,
        'feature_importances': feature_importance_dict,
        'chart_data': {
            'periods': chart_periods,
            'actuals': chart_actuals,
            'predictions': chart_preds
        }
    }
    
    metadata_path = os.path.join(model_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Model metadata saved to {metadata_path}")

if __name__ == '__main__':
    train_forecasting_model()
