import os
import json

def print_evaluation_report():
    metadata_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'models', 'model_metadata.json')
    
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found at {metadata_path}. Please run train_model.py first.")
        return

    with open(metadata_path, 'r') as f:
        data = json.load(f)

    print("==================================================")
    print("      NinoSense ML Model Evaluation Report        ")
    print("==================================================")
    print("\n1. Performance Metrics by Forecast Horizon:")
    print(f"{'Horizon':<12} | {'Train MAE':<10} | {'Test MAE':<10} | {'Test RMSE':<10} | {'Test R2':<8}")
    print("-" * 60)
    
    for step, metrics in data['metrics'].items():
        horizon_txt = f"{step.replace('tplus_', '')} Month(s) Out"
        print(f"{horizon_txt:<12} | {metrics['train_mae']:<10.4f} | {metrics['test_mae']:<10.4f} | {metrics['test_rmse']:<10.4f} | {metrics['test_r2']:<8.4f}")

    print("\n2. Feature Importances:")
    print(f"{'Feature Name':<20} | {'Importance Value':<16}")
    print("-" * 40)
    for feat, imp in list(data['feature_importances'].items())[:10]:
        print(f"{feat:<20} | {imp:<16.4f}")
    
    print("\nReport printed successfully.")

if __name__ == '__main__':
    print_evaluation_report()
