from fastapi import APIRouter, Request, HTTPException, Depends
from slowapi import Limiter
from typing import Union
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database.Database_functions import  add_transaction_details, validate_api_key
from predictors.transaction_predict import format_predictions, predict_fraud
from predictors.website_predict import format_data, predict_fraud_from_list
import random
import string
from fastapi.responses import JSONResponse

class Transaction(BaseModel):
    type: str
    amount: Union[float, int]
    # nameOrig: str
    oldbalanceOrg: Union[float, int]
    newbalanceOrig: Union[float, int]
    # nameDest: str
    oldbalanceDest: Union[float, int]
    newbalanceDest: Union[float, int]
    isFlaggedFraud: Union[float, int]
    mail: str


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
        val, confidence = format_data(
            v.url,
            v.credit_card_payment or None,
            v.money_back_payment or None,
            v.cash_on_delivery or None,
            v.crypto or None,
            v.free_contact_mails or None,
            v.logo_url or None,
)
        # Record details
        result = add_transaction_details(
            v.url,
            user_id,
            "NULL", "NULL", "NULL", "NULL", "NULL",
            val,
            "NULL",
            "NULL",
            "NULL",
            "Website",
            confidence,
            method="GUI"
        )
        return result

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
        data_list = [
            v.amount, v.oldbalanceOrg, v.newbalanceOrig,
            v.oldbalanceDest, v.newbalanceDest, v.isFlaggedFraud, v.type
        ]

        val, confidence = predict_fraud(format_predictions(data_list))

        # Generate transaction_id
        tx_id = generate_transaction_id()
        result = add_transaction_details(
        tx_id,
        user_id,
        v.amount, v.oldbalanceOrg, v.newbalanceOrig,
        v.oldbalanceDest, v.newbalanceDest,
        val,
        v.isFlaggedFraud,
        v.mail,
        v.type,
        "Transaction",
        confidence,
        method="API"
        )
        return result

    else:
        raise HTTPException(status_code=400, detail="Unknown type")
