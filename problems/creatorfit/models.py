from pydantic import BaseModel
from typing import Optional

class CreatorBase(BaseModel):
    """Base model for CreatorFit - define your creator models here"""
    name: str
    platform: str
    
    class Config:
        pass

# TODO: Add your models here
