import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

# Load EduReach dataset
df = pd.read_csv("edureach_improved_accessibility.csv")

# Features used for unsupervised ML
features = [
    "Nearest_School_Distance_km",
    "Has_School",
    "Has_PS",
    "Has_UPS",
    "Has_Composite",
    "Has_Madhyamik",
    "School_Count"
]

# Standardize features
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# Gaussian Mixture Model
model = GaussianMixture(
    n_components=3,
    random_state=42
)

# Generate ML clusters
df["ML_Cluster"] = model.fit_predict(X)

# Give meaningful pattern names based on the observed profiles
cluster_names = {
    0: "High Travel-Burden / No Local School",
    1: "Local School - Basic Coverage",
    2: "Local School - Broader Coverage"
}

df["ML_Pattern"] = df["ML_Cluster"].map(cluster_names)

# Save complete ML dataset
output_file = "edureach_ml_clusters.csv"
df.to_csv(output_file, index=False)

# Summary
print("EduReach ML clustering completed.")
print(f"Output file: {output_file}")
print(f"Total villages: {len(df)}")

print("\nML Cluster Summary:")
print(
    df.groupby(["ML_Cluster", "ML_Pattern"])
    .agg(
        Villages=("Village", "count"),
        Avg_Distance_km=("Nearest_School_Distance_km", "mean"),
        Avg_Accessibility=("Accessibility_Index", "mean")
    )
    .round(2)
    .to_string()
)

print("\nCluster 0 — High Travel-Burden / No Local School:")
print(
    df[df["ML_Cluster"] == 0][
        ["Village", "Nearest_School_Distance_km", "Accessibility_Index"]
    ]
    .sort_values("Nearest_School_Distance_km", ascending=False)
    .to_string(index=False)
)