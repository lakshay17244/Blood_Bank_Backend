#C:/Users/Jay/Anaconda3/python app.py

from flask import Flask,jsonify 
from flask_mysqldb import MySQL 

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dbms_123'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'ConnectGroup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["DEBUG"] = True

mysql = MySQL(app)


@app.route('/user/<username>')
def getUserDetailFromName(username):
	cur = mysql.connection.cursor()
	print(username)
	query = " SELECT * FROM user where Username='"+username+"'"
	# print(query)
	try: 
		cur.execute(query)
		results = cur.fetchall()[0]
		print(type(results))
		return results
	except:
		return jsonify("{Error: 'True'}")


@app.route('/table/<table>')
def getTableDetails(table):
	cur = mysql.connection.cursor()
	print(table)
	query = " SELECT * FROM "+ table
	# print(query)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except:
		results = "{Error: 'True'}"

	return jsonify(results)

app.run()