from pydantic import BaseModel
from typing import Union
from fastapi import APIRouter
from database.Database_functions import add_new_user, get_user_data, get_new_api_key, get_recent_transactions, clear_history
# from predictors.transaction_predict import 
from database.Database_functions import get_stats as gs
from database.Database_functions import get_all_transaction_details



router = APIRouter()



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


@router.post("/signup")
def signup(User: newUser):
    print(User)
    print(type(User))
    print(User.name)    
    return add_new_user(User.email, User.password, User.user_id, User.name)


@router.post("/signin")
def login(User: User):
    print(User)
    print(type(User))
    print(User.email)
    print(User.password)
    return get_user_data(User.password,User.email)




@router.post("/get_transaction_details")
def get_transaction(User: key):
    print(User.user_id, flush=True)
    return get_all_transaction_details(User.user_id) 

@router.post("/regenerate_key")
def generate_new_api_key(User: key):
    return get_new_api_key(User.user_id)

@router.post("/dashboard/stats")
def get_stats(User: key):
    return gs(User.user_id)

@router.post("/recent")
def get_recent(data: key):
    return get_recent_transactions(data.user_id)
    
@router.post("/clear_history")
def clear(data: key):
    return clear_history(data.user_id)