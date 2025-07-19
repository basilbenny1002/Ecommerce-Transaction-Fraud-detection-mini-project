from pydantic import BaseModel
from typing import Union, Optional
from fastapi import APIRouter
import random, string

from database.Database_functions import  add_transaction_details
from predictors.transaction_predict import predict_transaction
from predictors.website_predict import format_data, predict_fraud_from_list

router = APIRouter()


def genenerate_transaction_id():
  characters = string.ascii_letters + string.digits
  random_id_list = random.choices(characters, k=5)
  transaction_id = "".join(random_id_list)
  return transaction_id

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
    user_id: str
    url: str
    mail: Optional[str] = None
    credit_card_payment: Union[None, int]
    money_back_payment: Union[None, int]
    cash_on_delivery: Union[None, int]
    crypto: Union[None, int]
    free_contact_mails: Union[None, int]
    logo_url: Union[None, int]
    


@router.post("/predict/transaction")
def add_transaction(data: Transaction):
    pred, conf = predict_transaction(
            source=data.source,
            browser=data.browser,
            sex=data.sex,
            age=data.age,
            country_name=data.country_name,
            n_device_occur=data.n_device_occur,
            signup_month=data.signup_month,
            signup_day=data.signup_day,
            signup_day_name=data.signup_day_name,
            purchase_month=data.purchase_month,
            purchase_day=data.purchase_day,
            purchase_day_name=data.purchase_day_name,
            purchase_over_time=data.purchase_over_time
        )
    details = {"source": data.source, "browser": data.browser, "sex": data.sex, "age": data.age,
               "country_name": data.country_name, "n_device_occur": data.n_device_occur,
               "signup_month": data.signup_month, "signup_day": data.signup_day, "signup_day_name": data.signup_day_name,
               "purchase_month": data.purchase_month, "purchase_day": data.purchase_day, "purchase_day_name": data.purchase_day_name,
               "purchase_over_time": data.purchase_over_time}    
    return add_transaction_details(genenerate_transaction_id(), data.user_id, pred, "Transaction", conf, mail=data.mail, method="GUI", details=details)

@router.post("/predict/website")
def add_website(data: Website):
    val, confidence = format_data(data.url,data.credit_card_payment, data.money_back_payment, data.cash_on_delivery, data.crypto, data.free_contact_mails,data.logo_url)
    return add_transaction_details(data.url, data.user_id, val, "Website", confidence, mail=data.mail, method="GUI", details="Null" )
