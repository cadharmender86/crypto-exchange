from uuid import UUID
from pydantic import BaseModel, ConfigDict
class WalletAddressCreate(BaseModel):
    asset_id: UUID
    network: str
    address: str
    address_type: str = "DEPOSIT"
class WalletAddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    wallet_id: UUID
    asset_id: UUID
    network: str
    address: str
    address_type: str
    status: str

class WalletAddressGenerateRequest(BaseModel):
    asset: str
    network: str

class WalletAddressGenerateResponse(BaseModel):
    asset: str
    network: str
    address: str
    derivation_index: int
    newly_generated: bool    
