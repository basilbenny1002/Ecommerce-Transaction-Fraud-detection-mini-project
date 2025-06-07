import sqlite3
from fastapi.responses import JSONResponse
import random
import string
import smtplib
from email.mime.text import MIMEText
import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv
load_dotenv()


def generate_api_key(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))



def get_new_api_key(user_id: str):
    conn = None
    key = generate_api_key(16)
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("UPDATE USERS SET API_KEY = ? WHERE user_id = ?", (key, user_id))
        conn.commit()
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": "Failed"})
    else:
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "API_KEY": key})
    finally:
        if conn:
            conn.close()

def add_new_user(mail: str, password: str, user_id: str, name: str):
    conn = None
    try:
        API_KEY = generate_api_key(16)
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS USERS (user_id VARCHAR(255) primary key, name varchar(25), mail VARCHAR(255), password VARCHAR(255), API_KEY VARCHAR(255))") 
        
        # Check if mail exists (using parameterized query)
        cursor.execute("SELECT 1 FROM USERS WHERE mail = ?", (mail,))
        if cursor.fetchone():
            return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "User with this mail already exists."})

        cursor.execute("INSERT INTO USERS VALUES (?, ?, ?, ?, ?)", (user_id, name, mail, password, API_KEY))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error: User with this user_id already exists.")
        return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "User with this user_id already exists."})
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": f"Failed: {e}"})
    else:
        print("data inserted successfully")
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "API_KEY": API_KEY})    
    finally:
        if conn:
            conn.close()

def get_user_data(provided_password: str, mail: str ):
    conn = None
    if not mail:
        return JSONResponse(status_code=400, content={"Status_code": 400, "Message": "No user_id or mail provided"})
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE mail = ?", (mail,)) 
        data = cursor.fetchall()
        
        if not data:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "User not found"})
    except Exception as e:
        print(f"Some error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": f"Failed: {e}"})
    else:
        id, name, mail, password, api_key = data[0]
        if provided_password != password:
            return JSONResponse(status_code=401, content={"Status_code": 401, "Message": "Password is incorrect"})
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message": "Success", "UserID": id,"Name": name, "API_KEY": api_key})
    finally:
        if conn:
            conn.close()

   
def add_transaction_details(target, user_id, amount,  oldbalanceOrg,  newbalanceOrig,  oldbalanceDest,  newbalanceDest,  isFraud,  isFlaggedFraud, user_mail, type, target_type, confidence, method="GUI"):
    conn = None
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            target            VARCHAR(255) ,
            user_id           VARCHAR(255),
            amount            FLOAT,
            oldbalanceOrg     FLOAT,
            newbalanceOrig    FLOAT,
            oldbalanceDest    FLOAT,
            newbalanceDest    FLOAT,
            isFraud           INT,
            isFlaggedFraud    TEXT, /* Changed to TEXT to store "NULL" or integer */
            user_mail         VARCHAR(255),
            type              VARCHAR(255),
            method            VARCHAR(20), 
            target_type       VARCHAR(20), 
            confidence        FLOAT, /* Changed to FLOAT */
            TIMES DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # # Prepare confidence value
        # if isinstance(confidence, str) and '%' in confidence:
        #     parsed_confidence = float(confidence.replace('%', '')) / 100.0
        # elif isinstance(confidence, (int, float)):
        #     parsed_confidence = float(confidence)
        # else:
        #     parsed_confidence = None # Or a default float value like 0.0

        # Handle "NULL" strings for numeric/integer fields
        db_amount = None if amount == "NULL" else amount
        db_oldbalanceOrg = None if oldbalanceOrg == "NULL" else oldbalanceOrg
        db_newbalanceOrig = None if newbalanceOrig == "NULL" else newbalanceOrig
        db_oldbalanceDest = None if oldbalanceDest == "NULL" else oldbalanceDest
        db_newbalanceDest = None if newbalanceDest == "NULL" else newbalanceDest
        db_isFlaggedFraud = None if isFlaggedFraud == "NULL" else isFlaggedFraud

        cursor.execute("""
        INSERT INTO TRANSACTIONS (target,
            user_id, amount, oldbalanceOrg, newbalanceOrig,
            oldbalanceDest, newbalanceDest, isFraud,
            isFlaggedFraud, user_mail, type, method, target_type, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
        target, user_id, db_amount, db_oldbalanceOrg, db_newbalanceOrig,
        db_oldbalanceDest, db_newbalanceDest, isFraud,
        db_isFlaggedFraud, user_mail, type, method, target_type, confidence
        ))        
        conn.commit()
        if isFraud == 1:
            send_mail(user_mail, str(amount)) # Ensure amount is string for email
    except Exception as e:
        print(f"An error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": f"Failed: {e}"})
    else:
        print(isFraud, flush=True)
        return{"Status_code": 200, "Message": "Success", "Prediction": isFraud, "Confidence": confidence}
    finally:
        if conn:
            conn.close()

def get_transaction_details(user_id: str):
    # This function appears incomplete. If it's meant to be used, it needs implementation.
    # For now, just ensuring connection is managed if it were to be used.
    conn = None
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        # TODO: Implement actual logic to fetch and return transaction details
        # Example: cursor.execute("SELECT * FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
        # data = cursor.fetchall()
        # return data
    except Exception as e:
        print(f"An error occurred {e}")
    finally:
        if conn:
            conn.close()


def get_all_transaction_details(user_id: str):
    conn = None
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        # Ensure TRANSACTIONS table exists
        cursor.execute("""CREATE TABLE IF NOT EXISTS TRANSACTIONS (target VARCHAR(255), user_id VARCHAR(255), amount FLOAT, oldbalanceOrg FLOAT, newbalanceOrig FLOAT, oldbalanceDest FLOAT, newbalanceDest FLOAT, isFraud INT, isFlaggedFraud TEXT, user_mail VARCHAR(255), type VARCHAR(255), method VARCHAR(20), target_type VARCHAR(20), confidence FLOAT, TIMES DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("SELECT * FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
    except Exception as e:
        print(f"An error occurred {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": f"Failed {e}"})
    else:
        data = cursor.fetchall()
        print(data)
        if not data:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "User not found"}) 
        return JSONResponse(status_code=200, content={"Status_code": 200, "Message":"Success", "Content":{i: list(data[i]) for i in range(len(data))}})
    finally:
        if conn:
            conn.close()

def get_recent_transactions(user_id: str):
    conn = None
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        # Ensure TRANSACTIONS table exists
        cursor.execute("""CREATE TABLE IF NOT EXISTS TRANSACTIONS (target VARCHAR(255), user_id VARCHAR(255), amount FLOAT, oldbalanceOrg FLOAT, newbalanceOrig FLOAT, oldbalanceDest FLOAT, newbalanceDest FLOAT, isFraud INT, isFlaggedFraud TEXT, user_mail VARCHAR(255), type VARCHAR(255), method VARCHAR(20), target_type VARCHAR(20), confidence FLOAT, TIMES DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        # Limit the result to top 5 rows
        cursor.execute("SELECT * FROM TRANSACTIONS WHERE user_id = ? ORDER BY TIMES DESC LIMIT 5", (user_id,))
    except Exception as e:
        print(f"An error occurred {e}")
        return JSONResponse(
            status_code=500,
            content={"Status_code": 500, "Message": f"Failed {e}"}
        )
    else:
        data = cursor.fetchall()
        print(data)
        if not data:
            return JSONResponse(
                status_code=404,
                content={"Status_code": 404, "Message": "User not found"}
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "Status_code": 200,
                "Message": "Success",
                "Content": {i: list(data[i]) for i in range(len(data))}
            }
        )
    finally:
        if conn:
            conn.close()

def send_mail(mail_id, amount):
    print("Mail send successfully", flush=True)
    return #TODO uncomment to actually send the mail :DDDD
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(os.getenv("mail"), os.getenv("pass"))
    msg = MIMEText(f"Hey, your recent transaction of {amount} have been detected as a scam, please do the necessary steps")
    sender = "basilbenny1002@gmail.com"
    msg["Subject"] = "Fraudulent Transaction Alert"
    msg["From"] = sender
    msg["To"] = mail_id
    s.sendmail(sender, mail_id, msg.as_string())





def get_stats(user_id: str):
    conn = None
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        # Ensure TRANSACTIONS table exists
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS TRANSACTIONS (target VARCHAR(255), user_id VARCHAR(255), amount FLOAT, oldbalanceOrg FLOAT, newbalanceOrig FLOAT, oldbalanceDest FLOAT, newbalanceDest FLOAT, isFraud INT, isFlaggedFraud TEXT, user_mail VARCHAR(255), type VARCHAR(255), method VARCHAR(20), target_type VARCHAR(20), confidence FLOAT, TIMES DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
            total_rows = cursor.fetchone()[0]
        except Exception as e:
            total_rows = 0
        try:
            cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id = ? AND isFraud = 1", (user_id,))
            fraud_rows = cursor.fetchone()[0]
        except Exception as e:
            fraud_rows = 0
        try:
            cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id = ? AND method = ?", (user_id, "API"))
            api_rows = cursor.fetchone()[0]
        except:
            api_rows = 0
        return JSONResponse(status_code=200, content={"Status_code": 200, "total_checks": total_rows,"api_calls": api_rows, "frauds_detected": fraud_rows})
    except Exception as e:
        print(f"An error occurred {e}")
        return JSONResponse(status_code=404, content={"Status_code": 404, "Message": f"Failed: {e}"})
    finally:
        if conn:
            conn.close()
def clear_history(user_id: str):
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # # Optional: Ensure the table exists
        # cursor.execute("""CREATE TABLE IF NOT EXISTS TRANSACTIONS (
        #     target VARCHAR(255), 
        #     user_id VARCHAR(255), 
        #     amount FLOAT, 
        #     oldbalanceOrg FLOAT, 
        #     newbalanceOrig FLOAT, 
        #     oldbalanceDest FLOAT, 
        #     newbalanceDest FLOAT, 
        #     isFraud INT, 
        #     isFlaggedFraud TEXT, 
        #     user_mail VARCHAR(255), 
        #     type VARCHAR(255), 
        #     method VARCHAR(20), 
        #     target_type VARCHAR(20), 
        #     confidence FLOAT, 
        #     TIMES DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        # Execute the deletion
        cursor.execute("DELETE FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()

        if deleted_count == 0:
            return JSONResponse(status_code=404, content={"Status_code": 404, "Message": "No transactions found for this user."})
        else:
            return JSONResponse(status_code=200, content={"Status_code": 200, "Message": f"Successfully deleted {deleted_count} transaction(s)."})
    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"Status_code": 500, "Message": f"Failed: {e}"})
    finally:
        if conn:
            conn.close()

def validate_api_key(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    # Add your actual API key check here:
    user_id = getet_user_id_from_api_key(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_id

def getet_user_id_from_api_key(key: str):
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM USERS WHERE API_KEY = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()


# if __name__ == '__main__':
#     conn = None
#     print("Hello world")
#     try:
#         conn = sqlite3.connect('users.db') 
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM TRANSACTIONS")
#         data = cursor.fetchall()
#         print(data if data else "No data found")
#     finally:
#         if conn:
#             conn.close()
