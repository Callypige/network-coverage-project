from pydantic import BaseModel, Field

class OperatorCoverage(BaseModel):
    """Result for coverage"""
    two_g: bool = Field(alias="2G")
    three_g: bool = Field(alias="3G")
    four_g: bool = Field(alias="4G")
    
    model_config = {
        "populate_by_name": True  
    }

class AddressCoverage(BaseModel):
    """Result for an address"""
    orange: OperatorCoverage
    SFR: OperatorCoverage
    bouygues: OperatorCoverage
    Free: OperatorCoverage

class GeocodeResult(BaseModel):
    """Result for a geocoding request"""
    longitude: float
    latitude: float
    x_lambert93: float
    y_lambert93: float
    address_found: str