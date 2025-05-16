from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Database_functions import add_new_user, get_user_data, add_transaction_details, get_transaction_details
from typing import Union
from predict import predict_fraud



app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get("/")
async def root():
    return {"message": "Server up and running"}

class newUser(BaseModel):
    name: str
    email: str
    password: str
    user_id: str
class Transaction(BaseModel):
    user_id: str
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: float
    mail: str




@app.post("/signup/")
def signup(User: newUser):
    print(User)
    print(type(User))
    print(User.name)    
    return add_new_user(User.email, User.password, User.user_id)


@app.get("signin")
def login(password: str,user_id: Union[str, None] = Query(default=None), email: Union[str, None] = Query(default=None)):
    return get_user_data(password, user_id, email)

@app.post("/add_transaction_details")
def add_transaction(data: Transaction):
    return add_transaction_details(Transaction.user_id, Transaction.amount, Transaction.oldbalanceOrg, Transaction.newbalanceOrig, Transaction.oldbalanceDest, Transaction.newbalanceDest,predict_fraud([Transaction.amount, Transaction.oldbalanceOrg, Transaction.newbalanceOrig, Transaction.oldbalanceDest, Transaction.newbalanceDest, Transaction.isFlaggedFraud]), Transaction.isFlaggedFraud, Transaction.mail)

@app.get("/get_transaction_details")
def get_transaction(user_id: str):
    return get_transaction_details(user_id)