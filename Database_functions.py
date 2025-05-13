import sqlite3
import random
import string

def generate_api_key(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))




def add_new_user(mail: str, password: str, user_id: str):
    try:
        API_KEY = generate_api_key(16)
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS USERS (user_id VARCHAR(255) primary key, mail VARCHAR(255), password VARCHAR(255), API_KEY VARCHAR(255))") 
        cursor.execute(f"INSERT INTO USERS VALUES ('{user_id}', '{mail}', '{password}', '{API_KEY}')")
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Error: User with this user_id already exists.")
        return "User already exists"
    except Exception as e:
        print(f"Some error occurred {e}")
        return "Failed"
    else:
        print("data inserted successfully")
        return "Success"

def get_user_data(user_id: str):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM USERS WHERE user_id = '{user_id}'")
    except Exception as e:
        print(f"Some error occurred {e}")
        return "Failed"
    else:
        data = cursor.fetchall()



# cursor.execute('''INSERT INTO STUDENT VALUES ('Raju', '7th', 'A')''') 
# cursor.execute('''INSERT INTO STUDENT VALUES ('Shyam', '8th', 'B')''') 
# cursor.execute('''INSERT INTO STUDENT VALUES ('Baburao', '9th', 'C')''') 
  
# Display data inserted 
print("Data Inserted in the table: ") 
data=cursor.execute('''SELECT * FROM STUDENT''') 
for row in data: 
    print(row) 
  
# Commit your changes in the database     
conn.commit() 
  
# Closing the connection 
conn.close()

