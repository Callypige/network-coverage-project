import polars as pl

REQUIRED_COLUMNS = ['operator', 'x_lambert93', 'y_lambert93', '2G', '3G', '4G']

def load_coverage_measure_from_csv(path):
    """Load coverage measurement data from a CSV file."""
    df = pl.read_csv(path)
    # Rename columns
    df = df.rename({
        "Operateur": "operator",
        "x": "x_lambert93",
        "y": "y_lambert93"
    })
    # Convert 2G/3G/4G to booleans
    for col in ['2G', '3G', '4G']:
        df = df.with_columns(
            pl.col(col).cast(pl.Boolean)
        )
    return df

def validate_coverage_measure_dataframe(df):
    """Validate the structure of the coverage measurement DataFrame."""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            return False
    # Verify boolean column types
    for col in ['2G', '3G', '4G']:
        if df[col].dtype != pl.Boolean:
            return False
    return True

def get_unique_operators(df):
    """Get a list of unique operators from the DataFrame."""
    return df['operator'].unique().to_list()