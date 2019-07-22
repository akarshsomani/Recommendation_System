import mysql.connector
from models import config

mydb = mysql.connector.connect(**config.db_credentials)

print(mydb)
mycursor = mydb.cursor()
print("Users Datatype --")
mycursor.execute("show columns from users")
for i in mycursor:
  print(i)

print("Ratings Datatype --")
mycursor.execute("show columns from ratings")
for i in mycursor:
  print(i)

mydb.close()
