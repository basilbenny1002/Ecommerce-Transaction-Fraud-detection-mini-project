from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from Database_functions import add_new_user, get_user_data, add_transaction_details, get_transaction_details, get_new_api_key
from typing import Union
from predict import format_predictions, predict_fraud



app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    print("Exception:", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


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
    amount: Union[float, int]
    # nameOrig: str
    oldbalanceOrg: Union[float, int]
    newbalanceOrig: Union[float, int]
    # nameDest: str
    oldbalanceDest: Union[float, int]
    newbalanceDest: Union[float, int]
    isFlaggedFraud: Union[float, int]
    mail: str
class User(BaseModel):
    email: str   
    password: str
class key(BaseModel):
    user_id: str





@app.post("/signup/")
def signup(User: newUser):
    print(User)
    print(type(User))
    print(User.name)    
    return add_new_user(User.email, User.password, User.user_id, User.name)


@app.post("/signin/")
def login(User: User):
    print(User)
    print(type(User))
    print(User.email)
    print(User.password)
    return get_user_data(User.password,User.email)


@app.post("/predict/")
def add_transaction(data: Transaction):
    return add_transaction_details(data.user_id, data.amount, data.oldbalanceOrg, data.newbalanceOrig, data.oldbalanceDest, data.newbalanceDest,predict_fraud(format_predictions([data.amount, data.oldbalanceOrg, data.newbalanceOrig, data.oldbalanceDest, data.newbalanceDest, data.isFlaggedFraud, data.type])), data.isFlaggedFraud, data.mail, data.type)

@app.get("/get_transaction_details")
def get_transaction(user_id: str):
    print(user_id, flush=True)
    return get_transaction_details(user_id) 

@app.post("/regenerate_key/")
def generate_new_api_key(User: key):
    return get_new_api_key(User.user_id)