from pydantic import BaseModel
from typing import Optional

class LeadBase(BaseModel):
    """Base model for HotLead - define your lead models here"""
    email: str
    name: str
    
    class Config:
        # Add any configuration here
        pass

# TODO: Add your models here
# Example:
# class Lead(LeadBase):
#     id: Optional[str] = None
#     source: str
#     score: Optional[int] = None
