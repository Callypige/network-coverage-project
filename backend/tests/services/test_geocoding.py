import pytest
from services.geocoding import geocode_address, convert_gps_to_lambert93

class TestGeocoding:
    @pytest.mark.asyncio
    async def test_geocode_valid_address(self):
        """Test with a known address"""
        result = await geocode_address("Tour Eiffel, Paris")
        
        assert result is not None
        assert 'latitude' in result
        assert 'longitude' in result
        assert 'x_lambert93' in result
        assert 'y_lambert93' in result

        # Tour Eiffel approx
        assert 48.85 < result['latitude'] < 48.86
        assert 2.29 < result['longitude'] < 2.30
    
    @pytest.mark.asyncio
    async def test_geocode_invalid_address(self):
        """Test with an invalid address"""
        result = await geocode_address("adresse qui n'existe pas du tout xyz123")
        assert result is None

    @pytest.mark.asyncio
    async def test_geocode_empty_string(self):
        """Test with an empty string"""
        result = await geocode_address("")
        assert result is None
    
    def test_convert_gps_to_lambert93(self):
        """Test the conversion of coordinates"""
        # Tour Eiffel GPS
        x, y = convert_gps_to_lambert93(2.2945, 48.8584)

        # Verify Lambert93 coordinates
        assert 640000 < x < 660000  # Paris is around 650000 in X
        assert 6850000 < y < 6870000  # Paris is around 6860000 in Y

    @pytest.mark.asyncio
    async def test_geocode_returns_lambert93(self):
        """Verify that geocoding returns Lambert93 coordinates"""
        result = await geocode_address("1 rue de la Paix, Paris")
        
        assert result is not None
        assert 'x_lambert93' in result
        assert 'y_lambert93' in result
        
        # Verify that these are numbers
        assert isinstance(result['x_lambert93'], float)
        assert isinstance(result['y_lambert93'], float)