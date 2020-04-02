from flask import Flask 
from flask_mysqldb import MySQL 

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lakshay'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'ConnectGroup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/<name>')
def index(name):
    cur = mysql.connection.cursor()
    cur.execute(" SELECT * FROM user where Username='Shaine' ")
    results = cur.fetchall()
    print(results)
    return str(results)