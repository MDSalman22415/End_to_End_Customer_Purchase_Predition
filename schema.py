from pydantic import BaseModel,Field
from enum import Enum



class Productcategory(str, Enum):
    Fashion     = 'Fashion'
    Grocey      =  'Grocery'
    Home        =  'Home'
    Beauty      =  'Beauty'
    Electronics = 'Electronics'
    Sports      = 'Sports'
    
class gender(str,Enum):
    male    = 'Male'
    Female  = 'Female'
    Othrer  =  'Other'
    Unknown = 'Unknown'
    
class discount_used(str,Enum):
    Yes = 'Yes'
    No  = 'No'
    unknown =  'unknown'
    

    
class Ecommercefeatures(BaseModel):
    age: int = Field(..., ge=18, le=100)
    gender :gender
    income : float = Field(...,ge=100,le=20000)
    product_category : Productcategory
    browsing_time : float =  Field(...,ge=1,le=200)
    pages_viewed :  float = Field(...,ge=2,le=30)
    previous_purchases : float = Field(...,ge=2,le=80)
    discount_used : discount_used
    
    
class PredictionResponse(BaseModel):
    prediction : str