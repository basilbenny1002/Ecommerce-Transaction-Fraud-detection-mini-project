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
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed"})
    else:
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "API_KEY": key})

def add_new_user(mail: str, password: str, user_id: str, name: str):
    try:
        API_KEY = generate_api_key(16)
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS USERS (user_id VARCHAR(255) primary key, name varchar(25), mail VARCHAR(255), password VARCHAR(255), API_KEY VARCHAR(255))") 
        try:
            cursor.execute(f"SELECT 1 FROM USERS WHERE mail =  ?", (mail,))
            if cursor.fetchall:
                return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "User with this mail already exists."})
        except Exception as e:
                return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed{e}"})
    
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

def get_user_data(provided_password: str, mail: str ):
    if not mail:
        return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "No user_id or mail provided"})
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        query = f"SELECT * FROM USERS WHERE mail = '{mail}'"
        print(query, flush=True)
        cursor.execute(query) 
        data = cursor.fetchall()
        if not data:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "User not found"})
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed"})
    else:
        id, name, mail, password, api_key = data[0]
        print("password:" + password, flush=True)
        print("given password:" + provided_password, flush=True)
        if provided_password != password:
            return JSONResponse(status_code=401, content={"Status_code": 401, "Message": "Password is incorrect"})
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "UserID": id,"Name": name, "API_KEY": api_key})


def add_transaction_details(user_id, amount,  oldbalanceOrg,  newbalanceOrig,  oldbalanceDest,  newbalanceDest,  isFraud,  isFlaggedFraud, user_mail, type):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            user_id           VARCHAR(255),
            amount            FLOAT,
            oldbalanceOrg     FLOAT,
            newbalanceOrig    FLOAT,
            oldbalanceDest    FLOAT,
            newbalanceDest    FLOAT,
            isFraud           INT,
            isFlaggedFraud    INT,
            user_mail         VARCHAR(255),
            type              VARCHAR(255),
            TIMES DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        INSERT INTO TRANSACTIONS (
            user_id, amount, oldbalanceOrg, newbalanceOrig,
            oldbalanceDest, newbalanceDest, isFraud,
            isFlaggedFraud, user_mail, type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
        user_id, amount, oldbalanceOrg, newbalanceOrig,
        oldbalanceDest, newbalanceDest, isFraud,
        isFlaggedFraud, user_mail, type
        ))        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred {e}")
        return
    else:
        print(isFraud, flush=True)
        return{"Status_code": 200, "Message": "Success", "Prediction": isFraud}
def get_transaction_details(user_id: str):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        query = f"SELECT * FROM TRANSACTIONS WHERE user_id = '{user_id}'"
        print(query, flush=True)
        cursor.execute(query)
    except Exception as e:
        print(f"An error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed {e}"})
        
    else:
        data = cursor.fetchall()
        print(data)
        # cursor.execute("SELECT * FROM TRANSACTIONS")
        # print(cursor.fetchall(), flush=True)
        if not data:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "User not found"}) 
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message":"Success", "Content":{i: list(data[i]) for i in range(len(data))}})
        



if __name__ == '__main__':
    print("Hello world")
    conn = sqlite3.connect('users.db') 
    cursor = conn.cursor()
    query = f"SELECT * FROM TRANSACTIONS"
    cursor.execute(query)
    data = cursor.fetchall()
    if data:
        print(data)
    else:
        print("No data found")
    # print(cursor.fetchall())

    # print(get_transaction_details("8lvahlFzFzHMfBKS"))
        



