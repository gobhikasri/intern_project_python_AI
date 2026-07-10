import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("dataset/noaa_data.csv")

# Create a simple time index
df["Time"] = range(len(df))

# Plot ONI values
plt.figure(figsize=(12, 6))
plt.plot(df["Time"], df["Value"])

plt.title("Historical Oceanic Niño Index (ONI)")
plt.xlabel("Time")
plt.ylabel("ONI Value")
plt.grid(True)

# Save graph
plt.savefig("oni_trend.png")

print("Graph saved as oni_trend.png")

# Show graph
plt.show()