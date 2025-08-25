# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import logging
from pathlib import Path

from models import AddressCoverage, OperatorCoverage
from services.coverage_calculator import compute_coverage_for_point
from services.coverage_loader import load_coverage_measure_from_csv
from services.geocoding import geocode_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Network Coverage API",
    description="API to check mobile network coverage for multiple addresses",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== LOAD CSV ONCE AT MODULE LEVEL ==========
print("🚀 Loading coverage data...")
coverage_df = None

# Simple path checking
csv_path = Path("data/coverage_measure.csv")
if not csv_path.exists():
    csv_path = Path("coverage_measure.csv")  # Try root directory

if csv_path.exists():
    try:
        coverage_df = load_coverage_measure_from_csv(csv_path)
        print(f"✅ Loaded {len(coverage_df)} towers from {csv_path}")
        operators = coverage_df['operator'].unique().to_list()
        print(f"📊 Operators found: {operators}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        coverage_df = None
else:
    print(f"❌ CSV file not found at {csv_path.absolute()}")
# ====================================================

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Network Coverage API is running!",
        "coverage_data_loaded": coverage_df is not None,
        "towers_count": len(coverage_df) if coverage_df is not None else 0
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if coverage_df is not None else "unhealthy",
        "coverage_data_loaded": coverage_df is not None,
        "records_count": len(coverage_df) if coverage_df is not None else 0
    }

@app.post("/coverage", response_model=Dict[str, AddressCoverage])
async def check_coverage(addresses: Dict[str, str]) -> Dict[str, AddressCoverage]:
    """
    Check network coverage for multiple addresses.
    
    Args:
        addresses: Dict with id as key and address string as value
        
    Returns:
        Dict with id as key and coverage information as value
    """
    
    # Check if coverage data is loaded
    if coverage_df is None:
        logger.error("Coverage data not loaded")
        raise HTTPException(status_code=500, detail="Coverage data not available")
    
    if not addresses:
        raise HTTPException(status_code=400, detail="No addresses provided")
    
    results = {}
    
    for address_id, address in addresses.items():
        logger.info(f"📍 Processing {address_id}: {address}")
        
        try:
            # Step 1: Geocode the address
            geocode_result = await geocode_address(address)
            
            if geocode_result is None:
                logger.warning(f"❌ Cannot geocode: {address}")
                # Assign default AddressCoverage (no coverage) for this address_id
                results[address_id] = convert_coverage_to_model({})
                continue
            
            logger.info(f"📍 Found coordinates: Lambert93({geocode_result.x_lambert93:.2f}, {geocode_result.y_lambert93:.2f})")
            
            # Step 2: Calculate coverage
            coverage_dict = compute_coverage_for_point(
                geocode_result.x_lambert93,
                geocode_result.y_lambert93,
                coverage_df
            )
            
            # Step 3: Convert to Pydantic models
            results[address_id] = convert_coverage_to_model(coverage_dict)
            
        except Exception as e:
            logger.error(f"Error processing {address_id}: {str(e)}")
            # Assign default AddressCoverage (no coverage) for this address_id
            results[address_id] = convert_coverage_to_model({})

    return results

def convert_coverage_to_model(coverage_dict: Dict) -> AddressCoverage:
    """
    Convert coverage calculation result to AddressCoverage model.
    The calculator returns: {'Orange': {'2G': bool, '3G': bool, '4G': bool}, ...}
    """
    
    # Default no coverage
    default = OperatorCoverage(**{"2G": False, "3G": False, "4G": False})
    
    # Build the response
    return AddressCoverage(
        orange=OperatorCoverage(
            **{
                "2G": coverage_dict.get('Orange', {}).get('2G', False),
                "3G": coverage_dict.get('Orange', {}).get('3G', False),
                "4G": coverage_dict.get('Orange', {}).get('4G', False)
            }
        ) if 'Orange' in coverage_dict else default,
        
        SFR=OperatorCoverage(
            **{
                "2G": coverage_dict.get('SFR', {}).get('2G', False),
                "3G": coverage_dict.get('SFR', {}).get('3G', False),
                "4G": coverage_dict.get('SFR', {}).get('4G', False)
            }
        ) if 'SFR' in coverage_dict else default,
        
        bouygues=OperatorCoverage(
            **{
                "2G": coverage_dict.get('Bouygues', {}).get('2G', False),
                "3G": coverage_dict.get('Bouygues', {}).get('3G', False),
                "4G": coverage_dict.get('Bouygues', {}).get('4G', False)
            }
        ) if 'Bouygues' in coverage_dict else default,
        
        Free=OperatorCoverage(
            **{
                "2G": coverage_dict.get('Free', {}).get('2G', False),
                "3G": coverage_dict.get('Free', {}).get('3G', False),
                "4G": coverage_dict.get('Free', {}).get('4G', False)
            }
        ) if 'Free' in coverage_dict else default
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)