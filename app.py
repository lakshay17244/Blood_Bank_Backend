#C:/Users/Jay/Anaconda3/python app.py

from flask import Flask,jsonify,request
from flask_mysqldb import MySQL 
from datetime import date


#=============================================================================================#

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dbms_123'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'ConnectGroup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["DEBUG"] = True
mysql = MySQL(app)


#=============================================================================================#

@app.route('/', methods=['GET'])
def home():
	return "<h1>Hello World</h1>"


@app.route('/user/<username>')
def getUserDetailFromName(username):
	cur = mysql.connection.cursor()
	print_it(username)
	query = " SELECT * FROM user where Username='"+username+"'"
	# print_it(query)
	try: 
		cur.execute(query)
		results = cur.fetchall()[0]
		print_it(type(results))
		return results
	except:
		return jsonify("{Error: 'True'}")


@app.route('/table/<table>')
def getTableDetails(table):
	cur = mysql.connection.cursor()
	print_it(table)
	query = " SELECT * FROM "+ table
	# print_it(query)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except:
		results = "{Error: 'True'}"

	return jsonify(results)


#=============================================================================================#

@app.route('/createuser', methods=['POST'])
def createUser():

	#Get total number of users
	mycursor = mysql.connection.cursor()
	query = "SELECT count(*) FROM User"
	mycursor.execute(query)
	
	#New id as total users + 1
	id_ = mycursor.fetchall()[0]['count(*)'] + 1
	print_it(id_)
	
	#Print the acquired user details from request
	user = request.json['user']
	print_it(user)
	
	#Calculate age from given DOB
	dob = list(map(int,user['Dob'].split('-')))
	print_it(dob)
	user['Age'] = calculateAge(date(dob[0],dob[1],dob[2]))
	print_it(user['Age'])

	reponse = ""
	
	try:
		#Insert values in user table
		sqlFormula = "INSERT INTO user VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
		toPut = (id_,user["Type"],user["Username"],user["Phone"],user["Email"],user["Address"],user["Pincode"],user["Age"])
		print(sqlFormula,toPut)
		mycursor.execute(sqlFormula,toPut)
		mysql.connection.commit()


		#Insert values in password table
		sqlPass = "INSERT INTO passwords VALUES(%s,%s,%s)"
		toPut = (id_,user["Password"],user["Username"])
		mycursor.execute(sqlPass,toPut)
		mysql.connection.commit()
		

		#Insert values in Donor table
		if(user['Type']=="Donor"):
			query = "INSERT into available_donor values(%s,%s,%s,%s)"
			toPut = (id_,date.today(),user["Bloodgroup"],user["WTD"])
			mycursor.execute(query,toPut)
			mysql.connection.commit()

		#Make succesfull reponse
		reponse = "{'userid':%d, 'status': %d, 'message':'Success'"%(id_,200)
	
	except Exception as e:
		#Make response and print error
		print(e)
		reponse = "{'status': 401 ,'message': 'Error'}"

	#Send back the response
	return jsonify(reponse)


#=============================================================================================#

# Helper function to calculate age from DOB 
def calculateAge(birthDate): 
	today = date.today() 
	age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
	return age


#Helper function to print in DEBUG mode
def print_it(s):
	if(app.config["DEBUG"]):
		print(s)

#=============================================================================================#

#Command to run the app
app.run()