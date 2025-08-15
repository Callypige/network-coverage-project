import pytest
import polars as pl
from pathlib import Path
from services.coverage_loader import load_coverage_measure_from_csv
from services.coverage_calculator import compute_coverage_for_point, compute_distance

TEST_CSV_PATH = Path(__file__).parent.parent / "data" / "test_coverage_measure.csv"

class TestComputeDistance:
    """Tests for the compute_distance function"""
    
    def test_compute_distance_same_point(self):
        """Distance between the same point should be 0"""
        distance = compute_distance(100.0, 100.0, 100.0, 100.0)
        assert distance == 0.0
    
    def test_compute_distance_known_values(self):
        """Test with known distance values"""
        # Distance between (0, 0) and (3, 4) should be 5
        distance = compute_distance(0.0, 0.0, 3.0, 4.0)
        assert distance == 5.0
        
        # Distance between (0, 0) and (1, 1) should be sqrt(2)
        distance = compute_distance(0.0, 0.0, 1.0, 1.0)
        assert distance == pytest.approx(1.414213562373095)

class TestComputeCoverageForPoint:
    """Tests for the compute_coverage_for_point function"""
    
    @pytest.fixture
    def coverage_df(self):
        """Fixture providing the test coverage DataFrame"""
        return load_coverage_measure_from_csv(TEST_CSV_PATH)
    
    def test_compute_coverage_returns_correct_structure(self, coverage_df):
        """Test that the function returns the correct structure"""
        result = compute_coverage_for_point(102980.0, 6847973.0, coverage_df)
        
        # Should return a dict
        assert isinstance(result, dict)
        
        # Each operator should have 2G, 3G, 4G keys
        for operator in result:
            assert "2G" in result[operator]
            assert "3G" in result[operator]
            assert "4G" in result[operator]
            assert isinstance(result[operator]["2G"], bool)
            assert isinstance(result[operator]["3G"], bool)
            assert isinstance(result[operator]["4G"], bool)
    
    def test_compute_coverage_point_at_orange_site_1(self, coverage_df):
        """Test coverage for a point exactly at first Orange site"""
        # First Orange site: x=102980, y=6847973, 2G=1, 3G=1, 4G=0
        x, y = 102980.0, 6847973.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        # Should have coverage for Orange 2G and 3G but not 4G (distance = 0)
        assert result["Orange"]["2G"] is True
        assert result["Orange"]["3G"] is True
        assert result["Orange"]["4G"] is False  # Orange doesn't have 4G at this site
    
    def test_compute_coverage_point_at_bouygues_site(self, coverage_df):
        """Test coverage for a point exactly at Bouygues site"""
        # Bouygues site: x=103114, y=6848664, 2G=1, 3G=1, 4G=1
        x, y = 103114.0, 6848664.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        # Should have all coverage for Bouygues at this location
        assert result["Bouygues"]["2G"] is True
        assert result["Bouygues"]["3G"] is True  
        assert result["Bouygues"]["4G"] is True
    
    def test_compute_coverage_point_at_sfr_site(self, coverage_df):
        """Test coverage for a point exactly at SFR site"""
        # SFR site: x=103113, y=6848661, 2G=1, 3G=1, 4G=0
        x, y = 103113.0, 6848661.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        # Should have 2G and 3G coverage for SFR but not 4G
        assert result["SFR"]["2G"] is True
        assert result["SFR"]["3G"] is True
        assert result["SFR"]["4G"] is False  # SFR has no 4G at this site
    
    def test_compute_coverage_point_at_free_site(self, coverage_df):
        """Test coverage for a point exactly at Free site"""
        # Free site: x=129220, y=6848789, 2G=0, 3G=1, 4G=1
        x, y = 129220.0, 6848789.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        # Should have 3G and 4G coverage for Free but not 2G
        assert result["Free"]["2G"] is False  # Free has no 2G at this site
        assert result["Free"]["3G"] is True
        assert result["Free"]["4G"] is True
    
    def test_compute_coverage_point_far_from_all_sites(self, coverage_df):
        """Test coverage for a point very far from all sites"""
        # Point very far away
        x, y = 999999.0, 999999.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        # Should have no coverage for any operator
        for operator in result:
            assert result[operator]["2G"] is False
            assert result[operator]["3G"] is False
            assert result[operator]["4G"] is False
    
    def test_compute_coverage_with_small_radius(self, coverage_df):
        """Test coverage with very small radius"""
        # Use very small radius
        small_radius = {"2G": 1.0, "3G": 1.0, "4G": 1.0}
        x, y = 102980.0, 6847973.0  # Exact Orange site location
        result = compute_coverage_for_point(x, y, coverage_df, small_radius)
        
        # Should still have coverage since we're exactly on the site (distance = 0)
        assert result["Orange"]["2G"] is True
        assert result["Orange"]["3G"] is True
        assert result["Orange"]["4G"] is False
        
        # Now test with a point slightly away (10 meters)
        x, y = 102990.0, 6847983.0  # 10 units away
        result = compute_coverage_for_point(x, y, coverage_df, small_radius)
        
        # Should have no coverage with small radius
        for operator in result:
            assert result[operator]["2G"] is False
            assert result[operator]["3G"] is False
            assert result[operator]["4G"] is False
    
    def test_compute_coverage_with_large_radius(self, coverage_df):
        """Test coverage with very large radius - should cover everything"""
        large_radius = {"2G": 1000000.0, "3G": 1000000.0, "4G": 1000000.0}
        x, y = 102980.0, 6847973.0
        result = compute_coverage_for_point(x, y, coverage_df, large_radius)
        
        # Should have coverage everywhere the technology exists
        # Based on your data:
        # Orange: has 2G at sites 1&3, 3G at sites 1,2,3, 4G at site 2
        assert result["Orange"]["2G"] is True  # Sites 1 & 3 have 2G
        assert result["Orange"]["3G"] is True  # Sites 1, 2 & 3 have 3G
        assert result["Orange"]["4G"] is True  # Site 2 has 4G
        
        # SFR: has 2G and 3G, no 4G
        assert result["SFR"]["2G"] is True
        assert result["SFR"]["3G"] is True
        assert result["SFR"]["4G"] is False  # SFR has no 4G in data
        
        # Bouygues: has all technologies
        assert result["Bouygues"]["2G"] is True
        assert result["Bouygues"]["3G"] is True
        assert result["Bouygues"]["4G"] is True
        
        # Free: has 3G and 4G, no 2G
        assert result["Free"]["2G"] is False  # Free has no 2G in data
        assert result["Free"]["3G"] is True
        assert result["Free"]["4G"] is True
    
    def test_compute_coverage_with_default_radius(self, coverage_df):
        """Test that default radius values are applied correctly"""
        x, y = 102980.0, 6847973.0
        result1 = compute_coverage_for_point(x, y, coverage_df)
        result2 = compute_coverage_for_point(x, y, coverage_df, None)
        result3 = compute_coverage_for_point(x, y, coverage_df, {"2G": 30000.0, "3G": 5000.0, "4G": 10000.0})
        
        # All should return the same result
        assert result1 == result2 == result3
    
    def test_compute_coverage_includes_all_operators(self, coverage_df):
        """Test that all operators from the DataFrame are included in results"""
        x, y = 102980.0, 6847973.0
        result = compute_coverage_for_point(x, y, coverage_df)
        
        expected_operators = {"Orange", "SFR", "Bouygues", "Free"}
        actual_operators = set(result.keys())
        
        assert actual_operators == expected_operators
    
    def test_compute_coverage_empty_dataframe(self):
        """Test behavior with empty DataFrame"""
        empty_df = pl.DataFrame({
            'operator': [],
            'x_lambert93': [],
            'y_lambert93': [],
            '2G': [],
            '3G': [],
            '4G': []
        }, schema={
            'operator': pl.Utf8,
            'x_lambert93': pl.Float64,
            'y_lambert93': pl.Float64,
            '2G': pl.Boolean,
            '3G': pl.Boolean,
            '4G': pl.Boolean
        })
        
        result = compute_coverage_for_point(100000.0, 100000.0, empty_df)
        assert result == {}
    
    def test_compute_coverage_technology_specific_check(self, coverage_df):
        """Test specific technology availability at different sites"""
        # Test at Orange site 3 (has 2G, 3G but no 4G)
        x, y = 115635.0, 6799938.0
        small_radius = {"2G": 10.0, "3G": 10.0, "4G": 10.0}
        result = compute_coverage_for_point(x, y, coverage_df, small_radius)
        
        # Should have 2G and 3G but not 4G for Orange at this specific location
        assert result["Orange"]["2G"] is True
        assert result["Orange"]["3G"] is True
        assert result["Orange"]["4G"] is False
    
    def test_compute_coverage_between_sites(self, coverage_df):
        """Test coverage at a point between two close sites"""
        # Point between SFR (103113, 6848661) and Bouygues (103114, 6848664)
        x, y = 103113.5, 6848662.5
        
        # With small radius, should cover both nearby sites
        small_radius = {"2G": 10.0, "3G": 10.0, "4G": 10.0}
        result = compute_coverage_for_point(x, y, coverage_df, small_radius)
        
        # Should have SFR coverage (2G, 3G)
        assert result["SFR"]["2G"] is True
        assert result["SFR"]["3G"] is True
        assert result["SFR"]["4G"] is False
        
        # Should have Bouygues coverage (all technologies)
        assert result["Bouygues"]["2G"] is True
        assert result["Bouygues"]["3G"] is True
        assert result["Bouygues"]["4G"] is True
    
    def test_compute_coverage_realistic_3g_radius(self, coverage_df):
        """Test with realistic 3G radius (5km) from default settings"""
        # Point at Orange site 1
        x, y = 102980.0, 6847973.0
        
        # Use only 3G radius, others very small
        radius = {"2G": 1.0, "3G": 5000.0, "4G": 1.0}
        result = compute_coverage_for_point(x, y, coverage_df, radius)
        
        # With 5km 3G radius from Orange site 1, should reach other nearby sites
        # Distance from Orange site 1 to SFR site: ~sqrt((103113-102980)^2 + (6848661-6847973)^2) ≈ ~700m
        # Distance from Orange site 1 to Bouygues site: ~sqrt((103114-102980)^2 + (6848664-6847973)^2) ≈ ~700m
        
        # Should have 3G coverage from multiple operators within 5km
        assert result["Orange"]["3G"] is True  # At exact location
        assert result["SFR"]["3G"] is True     # Within 5km
        assert result["Bouygues"]["3G"] is True # Within 5km