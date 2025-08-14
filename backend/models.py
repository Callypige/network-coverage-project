from pydantic import BaseModel

class OperatorCoverage(BaseModel):
    """Result for an coverage"""
    # We use 2G, 3G, 4G in JSON
    two_g: bool
    three_g: bool
    four_g: bool
    
    class Config:
        # {"2G": true, "3G": true, "4G": false}
        fields = {
            'two_g': '2G',
            'three_g': '3G',
            'four_g': '4G'
        }

class AddressCoverage(BaseModel):
    """RResult for an address"""
    orange: OperatorCoverage
    SFR: OperatorCoverage
    bouygues: OperatorCoverage
    Free: OperatorCoverage