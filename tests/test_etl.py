import os
import pandas as pd
import pytest
from src.etl import run_etl, normalize_units

def test_unit_conversion():
    """
    Validates that tonnes ('t') convert correctly to kg (factor 1000) 
    and unrecognized units are blocked with a note.
    """
    data = {
        "facility_id": ["FAC_TEST_1", "FAC_TEST_2"],
        "year": [2021, 2021],
        "pollutant": ["Benzene", "Benzene"],
        "medium": ["Air", "Air"],
        "amount": [2.0, 50.0],
        "unit": ["t", "unknown_unit"],
        "source_reference": ["SRC-1", "SRC-2"]
    }
    df = pd.DataFrame(data)
    res = normalize_units(df)
    
    # Check tonne conversion (2.0 tonnes -> 2000.0 kg)
    assert res.loc[res['facility_id'] == 'FAC_TEST_1', 'normalized_amount'].values[0] == 2000.0
    
    # Check that unknown unit is blocked (results in None / NaN)
    assert pd.isna(res.loc[res['facility_id'] == 'FAC_TEST_2', 'normalized_amount'].values[0])

def test_trend_calculations_and_missing_years():
    """
    Validates Acceptance Test #1: 
    100 -> 20 reports an 80% decline, and missing years are preserved (not zero).
    """
    valid_df, trends_df = run_etl()
    
    # Check FAC_001 trends from the fixture
    fac1_trend = trends_df[trends_df['facility_id'] == 'FAC_001'].iloc[0]
    
    # 100 to 20 should result in -80.0% change and trigger the >=70% decline flag
    assert fac1_trend['percentage_change'] == -80.0
    assert fac1_trend['decline_gte_70_pct'] == True
    
    # Year 2020 was missing in the fixture for FAC_001, verify it is tracked as missing, not zero
    assert 2020 in fac1_trend['missing_years_in_range']

def test_idempotency(tmp_path):
    """
    Validates Acceptance Test #3:
    Repeated ETL run is idempotent (produces identical output results).
    """
    out_dir_1 = tmp_path / "run_1"
    out_dir_2 = tmp_path / "run_2"
    
    _, trends_1 = run_etl(output_dir=str(out_dir_1))
    _, trends_2 = run_etl(output_dir=str(out_dir_2))
    
    # Compare the dataframes to ensure they are identical
    pd.testing.assert_frame_equal(trends_1, trends_2)