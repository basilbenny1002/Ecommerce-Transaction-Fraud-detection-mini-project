from pydantic import BaseModel
from typing import Union
from fastapi import APIRouter
import random, string

from database.Database_functions import  add_transaction_details
from predictors.transaction_predict import format_predictions, predict_fraud
from predictors.website_predict import format_data, predict_fraud_from_list

router = APIRouter()


def genenerate_transaction_id():
  characters = string.ascii_letters + string.digits
  random_id_list = random.choices(characters, k=5)
  transaction_id = "".join(random_id_list)
  return transaction_id

class Transaction(BaseModel):
    user_id: str
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
    user_id: str
    url: str
    credit_card_payment: Union[None, int]
    money_back_payment: Union[None, int]
    cash_on_delivery: Union[None, int]
    crypto: Union[None, int]
    free_contact_mails: Union[None, int]
    logo_url: Union[None, int]
    



@router.post("/predict/transaction")
def add_transaction(data: Transaction):
    val, confidence = predict_fraud(format_predictions([data.amount, data.oldbalanceOrg, data.newbalanceOrig, data.oldbalanceDest, data.newbalanceDest, data.isFlaggedFraud, data.type]))
    return add_transaction_details(genenerate_transaction_id(), data.user_id, data.amount, data.oldbalanceOrg, data.newbalanceOrig, data.oldbalanceDest, data.newbalanceDest,val, data.isFlaggedFraud, data.mail, data.type, "Transaction", confidence, method="GUI")

@router.post("/predict/website")
def add_website(data: Website):
    val, confidence = format_data(data.url,data.credit_card_payment, data.money_back_payment, data.cash_on_delivery, data.crypto, data.free_contact_mails,data.logo_url)
    return add_transaction_details(data.url, data.user_id, "NULL","NULL", "NULL", "NULL", "NULL",val, "NULL", "NULL", "NULL", "Website", confidence, method="GUI" )
