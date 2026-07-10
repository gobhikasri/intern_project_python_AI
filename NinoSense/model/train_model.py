import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load NOAA ONI dataset
df = pd.read_csv("dataset/noaa_data.csv")

# Create Risk_Level column
def assign_risk(value):
    if value < 0.5:
        return "Low"
    elif value <= 1.5:
        return "Medium"
    else:
        return "High"

df["Risk_Level"] = df["Value"].apply(assign_risk)

# Features
X = df[["Year", "MonthNum", "Value"]]

# Target
y = df["Risk_Level"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Test accuracy
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy*100:.2f}%")

# Save model
joblib.dump(model, "model/model.pkl")

print("Model saved successfully!")