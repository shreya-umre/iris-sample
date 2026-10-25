import os
import json
import pandas as pd

def normalize_units(df):
    """
    Normalizes units (e.g., converts tonnes 't' to kilograms 'kg').
    Blocks unconvertible units with a descriptive reason.
    """
    df = df.copy()
    df['unit_clean'] = df['unit'].str.lower().str.strip()
    
    normalized_amounts = []
    normalization_notes = []
    
    for _, row in df.iterrows():
        unit = row['unit_clean']
        amount = row['amount']
        
        if unit in ['kg', 'kilograms', 'kilogram']:
            normalized_amounts.append(amount)
            normalization_notes.append("Native kg; no conversion needed")
        elif unit in ['t', 'tonnes', 'tonne']:
            # Conversion factor: 1 tonne = 1000 kg
            normalized_amounts.append(amount * 1000.0)
            normalization_notes.append("Converted from tonnes to kg (factor: 1000)")
        else:
            normalized_amounts.append(None)
            normalization_notes.append(f"Blocked: Unrecognized or unconvertible unit '{row['unit']}'")
            
    df['normalized_amount'] = normalized_amounts
    df['unit_note'] = normalization_notes
    return df

def run_etl(input_path="data/prtr_fixture.csv", output_dir="data"):
    """
    Executes the full PRTR ETL pipeline and computes trends.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}. Please generate the fixture first.")
        
    df = pd.read_csv(input_path)
    
    # Normalize units
    df_norm = normalize_units(df)
    
    # Filter valid records
    valid_df = df_norm.dropna(subset=['normalized_amount']).copy()
    
    # Save facility-year normalized table
    normalized_output_path = os.path.join(output_dir, "facility_year_normalized.csv")
    valid_df.to_csv(normalized_output_path, index=False)
    print(f"[ETL] Saved normalized table: {normalized_output_path}")
    
    # Initialize trend_results list properly
    trend_results = []
    group_cols = ['facility_id', 'pollutant', 'medium']
    
    for name, group in valid_df.groupby(group_cols):
        facility_id, pollutant, medium = name
        group = group.sort_values('year')
        
        years = group['year'].tolist()
        min_year = min(years)
        max_year = max(years)
        
        # Identify missing years in the sequence without turning them into zero
        expected_years = list(range(min_year, max_year + 1))
        missing_years = [y for y in expected_years if y not in years]
        
        baseline_row = group[group['year'] == min_year].iloc[0]
        latest_row = group[group['year'] == max_year].iloc[0]
        
        baseline_val = baseline_row['normalized_amount']
        latest_val = latest_row['normalized_amount']
        
        # Calculate percentage change
        if baseline_val > 0:
            pct_change = ((latest_val - baseline_val) / baseline_val) * 100.0
        else:
            pct_change = 0.0
            
        # Configurable indicative >= 70% decline flag
        is_70_percent_decline = pct_change <= -70.0
        
        trend_results.append({
            "facility_id": facility_id,
            "pollutant": pollutant,
            "medium": medium,
            "baseline_year": int(min_year),
            "baseline_amount_kg": float(baseline_val),
            "latest_year": int(max_year),
            "latest_amount_kg": float(latest_val),
            "percentage_change": round(pct_change, 2),
            "decline_gte_70_pct": bool(is_70_percent_decline),
            "missing_years_in_range": missing_years,
            "confidence_note": f"Baseline {min_year} to Latest {max_year}. Missing years explicitly preserved (not zero): {missing_years}"
        })
        
    trends_df = pd.DataFrame(trend_results)
    
    # Save trend reports in CSV and JSON formats
    trend_csv_path = os.path.join(output_dir, "audit_ready_trends.csv")
    trend_json_path = os.path.join(output_dir, "audit_ready_trends.json")
    
    trends_df.to_csv(trend_csv_path, index=False)
    with open(trend_json_path, 'w') as f:
        json.dump(trend_results, f, indent=4)
        
    print(f"[ETL] Saved audit-ready trends: {trend_csv_path} & {trend_json_path}")
    return valid_df, trends_df

if __name__ == "__main__":
    run_etl()