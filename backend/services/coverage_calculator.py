import polars as pl
from typing import Optional

def compute_coverage_for_point(x: float, y: float, df: pl.DataFrame, radius_by_tech: Optional[dict[str, float]] = None):
    """
    Calculates the coverage for a given point.
    Args:
        x, y: Lambert93 coordinates
        df: Polars DataFrame of antennas
        radius_by_tech: dict of radius per technology (in meters)
    If None, defaults to {"2G": 30000, "3G": 5000, "4G": 10000}.
    Returns:
        dict {operator: {2G: bool, 3G: bool, 4G: bool}}
    """
    if radius_by_tech is None:
        radius_by_tech = {"2G": 30000, "3G": 5000, "4G": 10000}
    
    # Calculate distance for ALL antennas once
    df_with_distance = df.with_columns([
        ((pl.col('x_lambert93') - x) ** 2 + (pl.col('y_lambert93') - y) ** 2).sqrt().alias('distance')
    ])
    
    operators = df['operator'].unique().to_list()
    result = {}
    
    for op in operators:
        op_df = df_with_distance.filter(pl.col('operator') == op)
        cover = {}
        
        for tech in ["2G", "3G", "4G"]:
            # Check if any antenna with this tech (=1) is within range
            has_coverage = op_df.filter(
                (pl.col(tech) == 1) &  # Has the technology
                (pl.col('distance') <= radius_by_tech[tech])  # Is within range
            ).height > 0
            
            cover[tech] = bool(has_coverage)
        
        result[op] = cover
    
    return result