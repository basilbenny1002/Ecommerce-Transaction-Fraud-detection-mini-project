import sqlite3

def add_new_user(mail: str, password: str, user_id: str):
    try:
        conn = sqlite3.connect('users.db') 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXIST USERS (user_id VARCHAR(255), mail VARCHAR(255), password VARCHAR(255))") 
        cursor.execute(f"INSERT INTO USERS VALUES ('{user_id}', '{mail}', '{password}')")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Some error occurred {e}")
    else:
        print("data inserted successfully")

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

