import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="1234",
  database="movie_data"
)

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
