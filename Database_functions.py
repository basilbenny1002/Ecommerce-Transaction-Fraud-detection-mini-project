import sqlite3
from fastapi.responses import JSONResponse
import random
import string

def generate_api_key(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_new_api_key(user_id: str):
    key = generate_api_key(16)
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute(f"UPDATE USERS SET API_KEY = '{key}' WHERE user_id = '{user_id}'")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Some error occurred {e}")
        return "Failed"
    else:
        return key

def add_new_user(mail: str, password: str, user_id: str, name: str):
    try:
        API_KEY = generate_api_key(16)
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS USERS (user_id VARCHAR(255) primary key, name varxhar(25), mail VARCHAR(255), password VARCHAR(255), API_KEY VARCHAR(255))") 
        cursor.execute(f"INSERT INTO USERS VALUES ('{user_id}', '{name}', '{mail}', '{password}', '{API_KEY}')")
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Error: User with this user_id already exists.")
        return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "User with this user_id already exists."})
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed"})
    else:
        print("data inserted successfully")
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "API_KEY": API_KEY})    

def get_user_data(provided_password: str, user_id: str = None, mail: str = None):
    if not user_id and not mail:
        return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "No user_id or mail provided"})
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM USERS WHERE user_id = '{user_id if user_id else mail}'") #TODO, change the logic
        data = cursor.fetchall()
        if not data:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "User not found"})
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed"})
    else:
        id, name, mail, password, api_key = data[0]
        if provided_password != password:
            return JSONResponse(status_code=401, content={"Status_code": 401, "Message": "Password is incorrect"})
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "UserID": id,"Name": name, "API_KEY": api_key})


def add_transaction_details(user_id, amount,  oldbalanceOrg,  newbalanceOrig,  oldbalanceDest,  newbalanceDest,  isFraud,  isFlaggedFraud,  type_CASH_OUT,  type_DEBIT,  type_PAYMENT,  type_TRANSFER, user_mail):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS TRANSACTIONS (user_id, varchar(255) foreign key references USERS(user_id), amount FLOAT, oldbalanceOrg FLOAT, newbalanceOrig FLOAT, oldbalanceDest FLOAT, newbalanceDest FLOAT, isFraud INT, isFlaggedFraud INT,user_mail VARCHAR(255))") 
        cursor.execute(f"INSERT INTO TRANSACTIONS VALUES ('{user_id}', '{amount}', '{oldbalanceOrg}', '{newbalanceOrig}', '{oldbalanceDest}', '{newbalanceDest}', '{isFraud}', '{isFlaggedFraud}', '{user_mail}')")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred {e}")
        return
    else:
        return{"Status_code": 200, "Message": "Success"}
def get_transaction_details(user_id: str):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM TRANSACTIONS WHERE user_id = '{user_id}'")
    except Exception as e:
        print(f"An error occurred {e}")
        return
    else:
        data = cursor.fetchall()
        if not data:
            return "User not found" 
        return {i: list(data[i]) for i in range(data)}




        



