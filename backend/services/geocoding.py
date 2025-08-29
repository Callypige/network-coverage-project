import aiohttp
from typing import Optional, List
import pyproj
import asyncio
import logging

from models import GeocodeResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds

class GeocodingError(Exception):
    """Custom exception for geocoding errors."""

async def geocode_address(address: str, session: Optional[aiohttp.ClientSession] = None) -> Optional[GeocodeResult]:
    """
    Géocode address with the data.gouv.fr API

    Args:
        address: The address to geocode
        session: Optional aiohttp session

    Returns:
        A GeocodeResult object or None if not found

    Raises:
        GeocodingError: If any error occurs during geocoding.
    """
    if not address or not address.strip():
        raise GeocodingError("Address is empty or invalid.")

    url = "https://api-adresse.data.gouv.fr/search/"
    params = {"q": address.strip(), "limit": 1}

    close_session = False
    if session is None:
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        session = aiohttp.ClientSession(timeout=timeout)
        close_session = True

    try:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise GeocodingError(f"HTTP error: {response.status}")

            try:
                data = await response.json()
            except Exception as e:
                raise GeocodingError(f"Error parsing JSON: {e}")

            if not data.get('features'):
                raise GeocodingError("No features found in response.")

            feature = data['features'][0]
            coords = feature['geometry']['coordinates']
            lon, lat = coords[0], coords[1]

            try:
                x_lambert93, y_lambert93 = convert_gps_to_lambert93(lon, lat)
            except Exception as e:
                raise GeocodingError(f"Error converting coordinates: {e}")

            return GeocodeResult(
                longitude=lon,
                latitude=lat,
                x_lambert93=x_lambert93,
                y_lambert93=y_lambert93,
                address_found=feature['properties']['label']
            )
    except asyncio.TimeoutError:
        raise GeocodingError("Request timed out.")
    except aiohttp.ClientError as e:
        raise GeocodingError(f"Client error: {e}")
    except Exception as e:
        raise GeocodingError(f"Unexpected error during geocoding: {e}")
    finally:
        if close_session:
            await session.close()

def convert_gps_to_lambert93(lon: float, lat: float) -> tuple:
    """Convert GPS coordinates (lon, lat) to Lambert 93 (x, y)"""
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
    x_lambert93, y_lambert93 = transformer.transform(lon, lat)
    return x_lambert93, y_lambert93

async def geocode_addresses(addresses: List[str]) -> List[Optional[GeocodeResult]]:
    """
    Geocode multiple addresses concurrently.

    Args:
        addresses: List of addresses to geocode

    Returns:
        List of GeocodeResult objects or None for each address
    """
    timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [geocode_address(address, session) for address in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Replace exceptions with None to match the expected return type
        cleaned_results = [
            result if isinstance(result, (GeocodeResult, type(None))) else None
            for result in results
        ]
        return cleaned_results
