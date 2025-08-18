from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app, convert_coverage_to_model

client = TestClient(app)

class TestMainAPI:
    """Tests for the main API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Network Coverage API is running!" in data["message"]
        assert "coverage_data_loaded" in data
        assert "towers_count" in data
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert "coverage_data_loaded" in data
        assert "records_count" in data
    
    def test_coverage_endpoint_no_addresses(self):
        """Test coverage endpoint with empty request"""
        response = client.post("/coverage", json={})
        assert response.status_code == 400
        assert "No addresses provided" in response.json()["detail"]
    
    @patch('main.coverage_df', None)
    def test_coverage_endpoint_no_csv_loaded(self):
        """Test coverage endpoint when CSV is not loaded"""
        response = client.post("/coverage", json={"id1": "Test address"})
        
        assert response.status_code == 500
        assert "Coverage data not available" in response.json()["detail"]
    
    @patch('main.geocode_address')
    @patch('main.compute_coverage_for_point')
    @patch('main.coverage_df')
    def test_coverage_endpoint_valid_address(self, mock_df, mock_compute, mock_geocode):
        """Test coverage endpoint with valid address"""
        # Mock CSV loaded
        mock_df.__bool__.return_value = True
        mock_df.__len__.return_value = 1000
        
        # Mock geocoding response
        mock_geocode.return_value = {
            'longitude': 2.2945,
            'latitude': 48.8584,
            'x_lambert93': 648237.0,
            'y_lambert93': 6862275.0,
            'address_found': 'Tour Eiffel, Paris'
        }
        
        # Mock coverage calculation
        mock_compute.return_value = {
            'Orange': {'2G': True, '3G': True, '4G': False},
            'SFR': {'2G': True, '3G': True, '4G': True},
            'Bouygues': {'2G': True, '3G': False, '4G': False},
            'Free': {'2G': False, '3G': True, '4G': True}
        }
        
        response = client.post("/coverage", json={
            "id1": "Tour Eiffel, Paris"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id1" in data
        # The API returns "2G", "3G", "4G" due to Pydantic Config.fields
        assert data["id1"]["orange"]["2G"]
        assert data["id1"]["orange"]["3G"]
        assert not data["id1"]["orange"]["4G"]
    
    @patch('main.geocode_address')
    @patch('main.coverage_df')
    def test_coverage_endpoint_invalid_address(self, mock_df, mock_geocode):
        """Test coverage endpoint with address that cannot be geocoded"""
        mock_df.__bool__.return_value = True
        mock_df.__len__.return_value = 1000
        
        mock_geocode.return_value = None
        
        response = client.post("/coverage", json={
            "id1": "adresse_inexistante_xyz123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id1" in data
        # The API returns "2G", "3G", "4G" due to Pydantic Config.fields
        assert not data["id1"]["orange"]["2G"]
        assert not data["id1"]["orange"]["3G"]
        assert not data["id1"]["orange"]["4G"]
        assert not data["id1"]["SFR"]["2G"]
        assert not data["id1"]["bouygues"]["2G"]
        assert not data["id1"]["Free"]["2G"]
    
    @patch('main.geocode_address')
    @patch('main.compute_coverage_for_point')
    @patch('main.coverage_df')
    def test_coverage_endpoint_multiple_addresses(self, mock_df, mock_compute, mock_geocode):
        """Test coverage endpoint with multiple addresses"""
        mock_df.__bool__.return_value = True
        mock_df.__len__.return_value = 1000
        
        # Different response for each call
        mock_geocode.side_effect = [
            {'x_lambert93': 648237.0, 'y_lambert93': 6862275.0},  # First address
            None,  # Second address fails
        ]
        
        mock_compute.return_value = {
            'Orange': {'2G': True, '3G': False, '4G': False}
        }
        
        response = client.post("/coverage", json={
            "id1": "Tour Eiffel, Paris",
            "id2": "invalid_address"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id1" in data
        assert "id2" in data
        
        # id1 should have coverage
        assert data["id1"]["orange"]["2G"]
        
        # id2 should have no coverage (geocoding failed)
        assert not data["id2"]["orange"]["2G"]
        assert not data["id2"]["orange"]["3G"]

class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_convert_coverage_to_model_with_data(self):
        """Test conversion from dict to Pydantic model with data"""
        coverage_dict = {
            'Orange': {'2G': True, '3G': True, '4G': False},
            'SFR': {'2G': True, '3G': False, '4G': True},
            'Bouygues': {'2G': False, '3G': False, '4G': False},
            'Free': {'2G': True, '3G': True, '4G': True}
        }
        
        result = convert_coverage_to_model(coverage_dict)
        
        # Check internal attributes (two_g, three_g, four_g)
        assert result.orange.two_g
        assert result.orange.three_g
        assert not result.orange.four_g
        
        assert result.SFR.two_g
        assert not result.SFR.three_g
        assert result.SFR.four_g
        
        assert result.Free.two_g
        assert result.Free.three_g
        assert result.Free.four_g
    
    def test_convert_coverage_to_model_empty_dict(self):
        """Test conversion with empty dict (creates empty coverage)"""
        result = convert_coverage_to_model({})
        
        # Check internal attributes
        assert not result.orange.two_g
        assert not result.orange.three_g
        assert not result.orange.four_g
        
        assert not result.SFR.two_g
        assert not result.bouygues.two_g
        assert not result.Free.two_g
    
    def test_convert_coverage_partial_operators(self):
        """Test conversion when some operators are missing"""
        coverage_dict = {
            'Orange': {'2G': True, '3G': True, '4G': True}
        }
        
        result = convert_coverage_to_model(coverage_dict)
        
        assert result.orange.two_g
        assert result.orange.three_g
        assert result.orange.four_g
        
        assert not result.SFR.two_g
        assert not result.bouygues.two_g
        assert not result.Free.two_g