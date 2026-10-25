import os
import pandas as pd

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "prtr_fixture.csv")

# 1. FAC_001: 100 -> 20 drop (80% decline), missing year 2020 (not zero)
# 2. FAC_002: Unit variations (kg vs t) to test unit normalization logic
data = {
    "facility_id": ["FAC_001", "FAC_001", "FAC_001", "FAC_002", "FAC_002", "FAC_002"],
    "year": [2018, 2019, 2021, 2018, 2019, 2021],
    "pollutant": ["Benzene", "Benzene", "Benzene", "Lead", "Lead", "Lead"],
    "medium": ["Air", "Air", "Air", "Water", "Water", "Water"],
    "amount": [100.0, 80.0, 20.0, 50000.0, 45.0, 40.0],
    "unit": ["kg", "kg", "kg", "kg", "t", "t"],  # Mix of kg and tonnes to test unit conversion
    "source_reference": ["EPA-2018", "EPA-2019", "EPA-2021", "GOV-2018", "GOV-2019", "GOV-2021"]
}

df = pd.DataFrame(data)
df.to_csv(file_path, index=False)

print(f"Successfully generated expanded fixture at: {file_path}")