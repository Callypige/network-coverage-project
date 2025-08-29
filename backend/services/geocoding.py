import aiohttp
from typing import Optional
import pyproj
import asyncio
import logging

from models import GeocodeResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds

async def geocode_address(address: str) -> Optional[GeocodeResult]:
    """
    Géocode address with the data.gouv.fr API

    Args:
        address: The address to geocode

    Returns:
        A GeocodeResult object or None if not found
    """
    if not address or not address.strip():
        return None

    url = "https://api-adresse.data.gouv.fr/search/"
    params = {"q": address.strip(), "limit": 1}

    timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"HTTP error: {response.status}")
                    return None

                try:
                    data = await response.json()
                except Exception as e:
                    logger.error(f"Error parsing JSON: {e}")
                    return None

                if not data.get('features'):
                    logger.info("No features found in response.")
                    return None

                feature = data['features'][0]
                coords = feature['geometry']['coordinates']
                lon, lat = coords[0], coords[1]

                try:
                    x_lambert93, y_lambert93 = convert_gps_to_lambert93(lon, lat)
                except Exception as e:
                    logger.error(f"Error converting coordinates: {e}")
                    return None

                return GeocodeResult(
                    longitude=lon,
                    latitude=lat,
                    x_lambert93=x_lambert93,
                    y_lambert93=y_lambert93,
                    address_found=feature['properties']['label']
                )

    except asyncio.TimeoutError:
        logger.error("Request timed out.")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Client error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during geocoding: {e}")
        return None

def convert_gps_to_lambert93(lon: float, lat: float) -> tuple:
    """Convert GPS coordinates (lon, lat) to Lambert 93 (x, y)

    Args:
        lon: The longitude in GPS coordinates
        lat: The latitude in GPS coordinates

    Returns:
        A tuple containing the x and y coordinates in Lambert 93
    """
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
    x_lambert93, y_lambert93 = transformer.transform(lon, lat)
    return x_lambert93, y_lambert93