import pytest
import polars as pl
from pathlib import Path
from services.coverage_loader import (
    load_coverage_measure_from_csv,
    validate_coverage_measure_dataframe,
    get_unique_operators
)
# Test data path
TEST_CSV_PATH = Path(__file__).parent.parent / "data" / "test_coverage_measure.csv"

class TestLoadCoverageMeasure:
    def test_load_coverage_measure_returns_dataframe(self):
        """Test loading coverage measurement data returns a DataFrame."""
        df = load_coverage_measure_from_csv(TEST_CSV_PATH)
        assert isinstance(df, pl.DataFrame)
    
    def test_load_coverage_measure_has_correct_columns(self):
        """Test loading coverage measurement data has correct columns."""
        df = load_coverage_measure_from_csv(TEST_CSV_PATH)
        expected_columns = ['operator', 'x_lambert93', 'y_lambert93', '2G', '3G', '4G']
        assert df.columns == expected_columns
    
    def test_load_coverage_measure_converts_to_boolean(self):
        """Test that the 2G, 3G, and 4G columns are converted to boolean."""
        df = load_coverage_measure_from_csv(TEST_CSV_PATH)
        assert df['2G'].dtype == pl.Boolean
        assert df['3G'].dtype == pl.Boolean
        assert df['4G'].dtype == pl.Boolean
    
    def test_load_coverage_measure_with_invalid_path(self):
        """Test loading coverage measurement data with an invalid path."""
        with pytest.raises(FileNotFoundError):
            load_coverage_measure_from_csv("file_that_does_not_exist.csv")

    def test_validate_dataframe_with_valid_data(self):
        """Test validation of DataFrame with valid data."""
        df = load_coverage_measure_from_csv(TEST_CSV_PATH)
        assert validate_coverage_measure_dataframe(df) is True
    
    def test_validate_dataframe_with_missing_column(self):
        """Test validation of DataFrame with missing columns."""
        bad_df = pl.DataFrame({
            'operator': ['Orange'],
            'x_lambert93': [652000]
        })
        assert validate_coverage_measure_dataframe(bad_df) is False
    
    def test_get_unique_operators(self):
        """Test getting unique operators from the DataFrame."""
        df = load_coverage_measure_from_csv(TEST_CSV_PATH)
        operators = get_unique_operators(df)
        # According to the CSV snippet
        assert set(operators) == {'Orange', 'Free', 'SFR', 'Bouygues'}