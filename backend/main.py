from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from models import AddressCoverage, OperatorCoverage

app = FastAPI(title="Network Coverage API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Test endpoint"""
    return {"message": "Network Coverage API is running!"}

@app.post("/coverage", response_model=Dict[str, AddressCoverage])
async def check_coverage(addresses: Dict[str, str]):
    """
    In : {"id1": "157 boulevard Mac Donald 75019 Paris"}
    Out : {"id1": {orange: {...}, SFR: {...}, bouygues: {...}}}
    """
    # Mock
    result = {}
    print(f"📨 Requête reçue : {addresses}") 
    
    for id_key, address in addresses.items():
        print(f"📍 Traitement de {id_key}: {address}")
        # Create objects with Pydantic models
        orange_coverage = OperatorCoverage(
            two_g=True,
            three_g=True,
            four_g=False
        )
        
        sfr_coverage = OperatorCoverage(
            two_g=True,
            three_g=True,
            four_g=True
        )
        
        bouygues_coverage = OperatorCoverage(
            two_g=True,
            three_g=False,
            four_g=False
        )

        free_coverage = OperatorCoverage(
            two_g=True,
            three_g=True,
            four_g=True
        )

        # Create object AddressCoverage
        address_result = AddressCoverage(
            orange=orange_coverage,
            SFR=sfr_coverage,
            bouygues=bouygues_coverage,
            Free=free_coverage
        )
        
        result[id_key] = address_result
    
    return result