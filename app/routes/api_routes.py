from fastapi import APIRouter, Request, HTTPException, Depends
from slowapi import Limiter
from typing import Union
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.routes.predict_routes import genenerate_transaction_id
from database.Database_functions import  add_transaction_details, validate_api_key
# from predictors.transaction_predict import format_predictions, predict_fraud
from predictors.transaction_predict import predict_transaction
from predictors.website_predict import format_data, predict_fraud_from_list
import random
import string
from fastapi.responses import JSONResponse

class Transaction(BaseModel):
    user_id: str
    source: str
    browser: str
    sex: str
    age: Union[int, float]
    country_name: str
    n_device_occur: Union[int, float]
    signup_month: int
    signup_day: int
    signup_day_name: str
    purchase_month: int
    purchase_day: int
    purchase_day_name: str
    purchase_over_time: Union[int, float]
    mail: Optional[str] = None  # mail can be null


class Website(BaseModel):
    url: str
    credit_card_payment: Union[None, int]
    money_back_payment: Union[None, int]
    cash_on_delivery: Union[None, int]
    crypto: Union[None, int]
    free_contact_mails: Union[None, int]
    logo_url: Union[None, int]
    

def generate_transaction_id():
  characters = string.ascii_letters + string.digits
  random_id_list = random.choices(characters, k=5)
  transaction_id = "".join(random_id_list)
  return transaction_id



limiter = Limiter(key_func=get_remote_address)
# Initialize router and rate limiter
router = APIRouter()

router.include_router(router)
# router.add_middleware(SlowAPIMiddleware)

# Pydantic models for input
class PredictRequest(BaseModel):
    type: str
    values: Union[Transaction, Website]

@router.post("/api/predict")
@limiter.limit("100/hour")
async def predict(request: Request, body: PredictRequest, user_id: str = Depends(validate_api_key)):
    # API key validation
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    t = body.type.lower()
    v = body.values

    if t == "website":
        # Required field url
        if not getattr(v, "url", None):
            raise HTTPException(status_code=400, detail="Missing required field: url")
        # Call your website handler logic
        val, confidence = format_data(v.url,v.credit_card_payment, v.money_back_payment, v.cash_on_delivery, v.crypto, v.free_contact_mails,v.logo_url)
        
        return add_transaction_details(v.url, v.user_id, val, "Website", confidence, mail=v.mail, method="API", details="Null" )

    elif t == "transaction":
        # Ensure required fields
        # required = [
        #     "amount", "oldbalanceOrg", "newbalanceOrig",
        #     "oldbalanceDest", "newbalanceDest", "isFlaggedFraud", "type"
        # ]
        # missing = [f for f in required if f not in v]
        # if missing:
        #     raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        # Predict fraud
        val, confidence = predict_transaction(
            source=v.source,
            browser=v.browser,
            sex=v.sex,
            age=v.age,
            country_name=v.country_name,
            n_device_occur=v.n_device_occur,
            signup_month=v.signup_month,
            signup_day=v.signup_day,
            signup_day_name=v.signup_day_name,
            purchase_month=v.purchase_month,
            purchase_day=v.purchase_day,
            purchase_day_name=v.purchase_day_name,
            purchase_over_time=v.purchase_over_time
        )
      
        details = {"source": v.source, "browser": v.browser, "sex": v.sex, "age": v.age,
               "country_name": v.country_name, "n_device_occur": v.n_device_occur,
               "signup_month": v.signup_month, "signup_day": v.signup_day, "signup_day_name": v.signup_day_name,
               "purchase_month": v.purchase_month, "purchase_day": v.purchase_day, "purchase_day_name": v.purchase_day_name,
               "purchase_over_time": v.purchase_over_time}    
        result = add_transaction_details(genenerate_transaction_id(), v.user_id, val, "Transaction", confidence, mail=v.mail, method="API", details=details)
        return result

    else:
        raise HTTPException(status_code=400, detail="Unknown type")
