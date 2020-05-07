from flask import Flask,jsonify,request
from flask_mysqldb import MySQL 
from datetime import date
from flask_cors import CORS
import logging
import sys
import mysql.connector
from os import environ
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,jwt_optional,
    get_jwt_identity
)

#=============================================================================================#

app = Flask(__name__)

# Enable Logging for Heroku
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# Enable CORS
CORS(app)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config["DEBUG"] = True

# =========================== LOCAL SQL SERVER ===========================
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_DB'] = 'ConnectGroup'
# app.config['MYSQL_PASSWORD'] = 'lakshay'
# app.config['MYSQL_PASSWORD'] = 'dbms_123'


# =========================== REMOTE SQL SERVER ===========================
# app.config['MYSQL_USER'] = 'swMUYUcOTM'
# app.config['MYSQL_HOST'] = 'remotemysql.com'
# app.config['MYSQL_DB'] = 'swMUYUcOTM'
# app.config['MYSQL_PASSWORD'] = 'LlyHn4U47w'


# =========================== HEROKU APP ===========================
# For LOCAL heroku server dev
# app.config.from_object('config')

# PRODUCTION
app.config['MYSQL_USER'] = environ.get('MYSQL_USER')
app.config['MYSQL_HOST'] = environ.get('MYSQL_HOST')
app.config['MYSQL_DB'] = environ.get('MYSQL_DB')
app.config['MYSQL_PASSWORD'] = environ.get('MYSQL_PASSWORD')
app.config['JWT_SECRET_KEY'] = environ.get('JWT_SECRET_KEY')


# =========================== JWT ===========================
jwt = JWTManager(app)

# Connect DB
mysql = MySQL(app)


#=============================================================================================#


@app.route('/')
def home():
	return "<h1>This is the backend for our DBMS Project - Blood Bank Management System</h1>"


@app.route('/table/<table>')
def getTableDetails(table):
	#To see updated tables, just for development purpose
	cur = mysql.connection.cursor()
	print_it(table)
	query = " SELECT * from "+ table
	# print_it(query)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E)}

	return jsonify(results)


#=============================================================================================#

# Working
@app.route('/getWTDDonors/<BG>')
def getWTDDonors(BG):
	cur = mysql.connection.cursor()
	query = """select distinct user.Email from available_donor join user on available_donor.UserID = user.UserID
				where available_donor.WillingToDonate=1
				and available_donor.BloodGroup="%s"	"""%(BG)
	# print_it(query)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E)}
	return jsonify(results)



@app.route('/profilepic/<uid>')
def getpp(uid):
	cur = mysql.connection.cursor()
	query = " SELECT * from Profile_Picture WHERE UserID=%s"%(uid)
	# print_it(query)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E)}

	return jsonify(results)


# Working / Uses Triple join!
@app.route('/getAppointment',methods=['POST'])
def getApp():
	UserID = request.json['UserID']
	#SEND request.json['Date'] for date specific query 
	response = ""
	cur = mysql.connection.cursor()	
	try:
		query = """ SELECT Appointment.*,user.Username as Name,user.Phone,available_donor.BloodGroup FROM 
					Appointment join user on appointment.UserID=user.UserID 
					join available_donor on available_donor.UserID=user.UserID
					WHERE DCID=(select DCID from donation_centers_employee where UserID=%s)"""%(UserID)
		if("Date" in request.json.keys()):
			query = query + ' AND Appointment.DATE="%s"'%(request.json['Date'])
		cur.execute(query)
		response = cur.fetchall()

	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(response)


# Working / Uses Join
@app.route('/getDonorAppointments/<UserID>')
def getDonorAppointments(UserID):
	cur = mysql.connection.cursor()
	query = "SELECT * FROM appointment join donation_centers on appointment.DCID = donation_centers.DCID where UserID=%s"%(UserID)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E),'status':401}

	return jsonify(results)


# Working
@app.route('/makeAppointment',methods = ['POST'])
def makeApp():
	dcid = request.json['DCID']
	uid = request.json['UserID']
	date = request.json['Date']

	response = ""
	cur = mysql.connection.cursor()	

	try:
		query = "SELECT count(*) FROM Appointment"
		cur.execute(query)
		aid = cur.fetchall()[0]['count(*)'] + 1
		print_it(aid)

		# BEGIN TRANSACTION
		cur.execute("BEGIN")

		query = "INSERT INTO Appointment VALUES(%s,%s,%s,%s)"
		toPut = (aid,uid,dcid,date)
		cur.execute(query,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working / Uses Transaction
@app.route('/removeemergencyrequirement',methods = ['POST'])
def removeemergencyrequirement():
	UserID = request.json['UserID']
	EID = request.json['EID']

	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")

		#DELETE 
		subquery = """SELECT * FROM emergencyrequirements where 
					DoctorID in (Select UserID from hospital_employee where HID = (Select HID from hospital_employee where UserID=%s))
					and
					EID=%s"""%(UserID,EID)
		print(subquery)
		mycursor.execute(subquery)
		subresult = mycursor.fetchall()
		print(subresult)
		if(len(subresult) > 0):
			sqlFormula = "DELETE from emergencyrequirements where EID=%s"%(EID)
			mycursor.execute(sqlFormula)

			# If no exception, then COMMIT the transaction
			mysql.connection.commit()
			#Make successful response
			response = {'status': 200, 'message':'Success!'}
		else:
			return jsonify({'Error': 'True','message': 'Wrong EID!'})
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)




# Working / Uses Transaction
@app.route('/addemergencyrequirement',methods = ['POST'])
def addemergencyrequirement():
	BloodNeeded = request.json['BloodNeeded']
	DateRecieved = request.json['DateRecieved']
	DoctorID = request.json['DoctorID']

	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		sqlFormula = "Select max(EID)+1 as EID from emergencyrequirements"
		mycursor.execute(sqlFormula)
		EID = mycursor.fetchall()[0]['EID']
		if EID is None:
			EID=1
		#Insert values in patients_list table
		sqlFormula = "INSERT INTO emergencyrequirements values (%s,%s,%s,%s)"
		toPut = (EID,BloodNeeded,DoctorID,DateRecieved)
		mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success!'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working / Uses join
@app.route('/getDonorERNearby/<UserID>')
def getDonorERNearby(UserID):
	cur = mysql.connection.cursor()
	query = """	SELECT * FROM emergencyrequirements join hospital on hospital.HID=(select HID from hospital_employee where UserID=emergencyrequirements.DoctorID)
				where hospital.Pincode = (select Pincode from user where UserID=%s)
                and emergencyrequirements.BloodNeeded=(select BloodGroup from available_donor where UserID=%s)
				order by emergencyrequirements.DateRecieved asc"""%(UserID,UserID)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E),'status':401}

	return jsonify(results)

# Working / Uses Join
@app.route('/getDonorERAll/<UserID>')
def getDonorERAll(UserID):
	cur = mysql.connection.cursor()
	query = """	SELECT * FROM emergencyrequirements join hospital on 
				hospital.HID=(select HID from hospital_employee where UserID=emergencyrequirements.DoctorID)
				where emergencyrequirements.BloodNeeded=(select BloodGroup from available_donor where UserID=%s)
				order by emergencyrequirements.DateRecieved asc"""%(UserID)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E),'status':401}

	return jsonify(results)


# Working
@app.route('/getemergencyrequirements/<UserID>')
def getemergencyrequirements(UserID):
	cur = mysql.connection.cursor()
	query = "SELECT * FROM emergencyrequirements where DoctorID in (Select UserID from hospital_employee where HID = (Select HID from hospital_employee where UserID=%s))"%(UserID)
	results = ""
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as E:
		results = {'Error': str(E),'status':401}

	return jsonify(results)



# Working / Uses Transaction
@app.route('/withdrawBlood',methods = ['POST'])
def withdrawBlood():
	BloodGroup = request.json['BloodGroup']
	BBID = request.json['BBID']

	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		sqlFormula = """ update donated_blood 
						set available=2
						where BloodGroup="%s" 
						and DCID in (Select DCID from donation_centers where BBID=%s) 
						and available=1
						order by DateRecieved asc limit 1;"""%(BloodGroup,BBID)
		mycursor.execute(sqlFormula)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)



# Working /Complex Query
@app.route('/checkBloodAvailabilityNearby/<BloodGroup>/<UserID>')
def checkBloodAvailabilityNearby(BloodGroup,UserID):
	cur = mysql.connection.cursor()
	results = ""
	
	try: 

		subquery = "SELECT Pincode FROM hospital where HID = (select HID from hospital_employee where UserID=%s)"%UserID
		cur.execute(subquery)
		Pincode = cur.fetchall()[0]["Pincode"]
		query = """ select blood_bank.Name,blood_bank.BBID,blood_bank.Address,blood_bank.Pincode,count(donated_blood.Amount) as Amount 
				from blood_bank,donated_blood 
				where 
				BBID =  (select BBID FROM donation_centers where DCID=donated_blood.DCID)
				and
				donated_blood.Available = 1 and donated_blood.BloodGroup="%s" and blood_bank.Pincode="%s"
				group by blood_bank.BBID """%(BloodGroup,Pincode)
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)



# Working /Complex Query
@app.route('/checkBloodAvailability/<BloodGroup>')
def checkBloodAvailability(BloodGroup):
	cur = mysql.connection.cursor()
	results = ""
	query = """ select blood_bank.Name,blood_bank.BBID,blood_bank.Address,blood_bank.Pincode,count(donated_blood.Amount) as Amount 
				from blood_bank,donated_blood 
				where 
				BBID =  (select BBID FROM donation_centers where DCID=donated_blood.DCID)
				and
				donated_blood.Available = 1 and donated_blood.BloodGroup="%s"
				group by blood_bank.BBID """%(BloodGroup)
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)



# Working / Uses Transaction
@app.route('/addPatient',methods = ['POST'])
def addPatient():
	BloodGroup = request.json['BloodGroup']
	AdmissionDate = request.json['AdmissionDate']
	UserID = request.json['UserID']
	HID = request.json['HID']

	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		sqlFormula = "Select max(PID)+1 as PID from patients_list"
		mycursor.execute(sqlFormula)
		PID = mycursor.fetchall()[0]['PID']
		if PID is None:
			PID=1
		#Insert values in patients_list table
		sqlFormula = "INSERT INTO patients_list values (%s,%s,%s,%s,%s)"
		toPut = (PID,UserID,AdmissionDate,BloodGroup,HID)
		mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working / Uses Transaction
@app.route('/removePatient',methods = ['POST'])
def removePatient():
	PID = request.json['PID']
	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")

		#Delete row in patients_list table
		sqlFormula = "DELETE FROM patients_list where PID = %s"%(PID)
		mycursor.execute(sqlFormula)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}

	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)

# Working
@app.route('/getPatientDetailsUnderYou/<UserID>')
def getPatientDetailsUnderYou(UserID):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM patients_list where HID = (SELECT HID from hospital_employee where UserID = %s) and UserID=%s"%(UserID,UserID)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getPatientDetails/<userId>')
def getPatientDetails(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM patients_list where HID = (SELECT HID from hospital_employee where UserID = %s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)

# Working
@app.route('/sendBloodToBloodBank',methods = ['POST'])
def sendBloodToBloodBank():
	DCID = request.json['DCID']
	response = ""
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		#Update values in donation_centers table
		sqlFormula = "Update Donated_Blood set Available=1 where DCID=%s and Available=0"%(DCID)
		mycursor.execute(sqlFormula)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)

# Working / Uses Transaction
@app.route('/updateH',methods = ['POST'])
def updateH():
	HID = request.json['HID']
	Name = request.json['Name']
	Address = request.json['Address']
	Pincode = request.json['Pincode']

	response = ""
	
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		#Update values in donation_centers table
		sqlFormula = "UPDATE Hospital SET Name=%s,Address=%s,Pincode=%s WHERE HID=%s"
		toPut = (Name,Address,Pincode,HID)
		mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working / Uses Transaction
@app.route('/updateBB',methods = ['POST'])
def updateBB():
	BBID = request.json['BBID']
	Name = request.json['Name']
	Address = request.json['Address']
	Pincode = request.json['Pincode']
	TotalCapacity = request.json['TotalCapacity']
	CapacityLeft = request.json['CapacityLeft']
	response = ""
	
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		#Update values in donation_centers table
		sqlFormula = "UPDATE Blood_Bank SET Name=%s,Address=%s,Pincode=%s,TotalCapacity=%s,CapacityLeft=%s WHERE BBID=%s"
		toPut = (Name,Address,Pincode,TotalCapacity,CapacityLeft,BBID)
		mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working / Uses Transaction
@app.route('/updateDC',methods = ['POST'])
def updateDC():
	DCID = request.json['DCID']
	Name = request.json['Name']
	Address = request.json['Address']
	Pincode = request.json['Pincode']

	response = ""
	
	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		#Update values in donation_centers table
		sqlFormula = "UPDATE Donation_Centers SET Name=%s,Address=%s,Pincode=%s WHERE DCID=%s"
		toPut = (Name,Address,Pincode,DCID)
		mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working
@app.route('/getBBStoredBlood/<userId>')
def getBBStoredBlood(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = """SELECT BloodGroup,count(*) as Amount FROM Donated_Blood where 
				Available=1
				and
				DCID in (Select DCID from Donation_Centers where BBID = (select BBID from Blood_Bank_Employee where UserID=%s))
				group by BloodGroup"""%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getHDetails/<userId>')
def getHDetails(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM Hospital where HID=(select HID from Hospital_Employee where UserID=%s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getBBDetails/<userId>')
def getBBDetails(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM Blood_Bank where BBID=(select BBID from Blood_Bank_Employee where UserID=%s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getDCDetails/<userId>')
def getDCDetails(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM Donation_Centers where DCID=(select DCID from Donation_Centers_Employee where UserID=%s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working / Uses twice nested query
@app.route('/getAssociatedDonationCenter/<UserID>')
def getAssociatedDonationCenter(UserID):
	cur = mysql.connection.cursor()
	results = ""
	query = "Select * from Donation_Centers where DCID in (SELECT DCID FROM Donation_Centers where BBID = (Select BBID from Blood_Bank_Employee where UserID=%s))"%(UserID)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working / Uses twice nested query
@app.route('/getAssociatedBloodBank/<userId>')
def getAssociatedBloodBank(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "Select * from Blood_Bank where BBID = (Select BBID from Donation_Centers where DCID= (SELECT DCID FROM Donation_Centers_Employee where UserID=%s))"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getDonatedBlood/<userId>')
def getDonatedBlood(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "SELECT * FROM Donated_Blood where DCID=(select DCID from Donation_Centers_Employee where UserID=%s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getbbemployees/<userId>')
def gbbe(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "Select * from Blood_Bank_Employee where BBID = (SELECT BBID FROM Blood_Bank_Employee where UserID=%s)"%(userId)		
	try: 
		cur.execute(query)
		results = cur.fetchall()
		for i in range(0,len(results)):
			subquery = "Select * from User where UserID=%s"%(results[i]["UserID"])
			cur.execute(subquery)
			userDetails = cur.fetchall()[0]
			results[i].update(userDetails)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/gethsemployees/<userId>')
def ghse(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "Select * from Hospital_Employee where HID = (SELECT HID FROM Hospital_Employee where UserID=%s)"%(userId)
	try: 
		cur.execute(query)
		results = cur.fetchall()
		for i in range(0,len(results)):
			subquery = "Select * from User where UserID=%s"%(results[i]["UserID"])
			cur.execute(subquery)
			userDetails = cur.fetchall()[0]
			results[i].update(userDetails)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)


# Working
@app.route('/getdcemployees/<userId>')
def gdce(userId):
	cur = mysql.connection.cursor()
	results = ""
	query = "Select * from Donation_Centers_Employee where DCID = (SELECT DCID FROM Donation_Centers_Employee where UserID=%s)"%(userId)	
	try: 
		cur.execute(query)
		results = cur.fetchall()
		for i in range(0,len(results)):
			subquery = "Select * from User where UserID=%s"%(results[i]["UserID"])
			cur.execute(subquery)
			userDetails = cur.fetchall()[0]
			results[i].update(userDetails)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	return jsonify(results)



@app.route('/enrollpatient',methods = ['POST'])
def enrollPatient():

	uid = request.json['UserID']
	ad_date = request.json['AdmissionDate']
	hid = request.json['HID']
	blood_need = request.json['BloodNeeded']
	
	query = "SELECT HID FROM Hospital_Employee where UserID=%s"%(uid)
	response = ""
	
	try: 
		cur = mysql.connection.cursor()
		cur.execute(query)
		results = cur.fetchall()

		if(len(results)==0):
			return jsonify({'Error': 'True','message':'Not a hospital staff user'})
		else:
			query = "SELECT count(*) FROM Patients_List"
			cur.execute(query)

			id_ = cur.fetchall()[0]['count(*)'] + 1
			print_it(id_)

			sqlFormula = "INSERT INTO Patients_List VALUES(%s,%s,%s,%s,%s)"
			toPut = (id_,uid,ad_date,blood_need,hid)
			cur.execute(sqlFormula,toPut)
			mysql.connection.commit()

			response = {'patientID':id_, 'status': 200, 'message':'Success'}
	
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working
@app.route('/rmvemployee',methods = ['POST'])
def rmvEmp():
	userId = request.json['UserID']
	place = request.json['place']

	cur = mysql.connection.cursor()
	query = " SELECT * FROM User where UserID=%s"%(userId)

	try: 
		cur.execute(query)
		user = cur.fetchone()
		if(user is None):
			return jsonify({'status':401,'Error': 'True','message':'''UserID Doesn't Exist'''})
		elif(user['Type']=='Donor'):
			return jsonify({'status':401,'Error': 'True','message':'User is not of type Admin!'})
		else:
			
			if(place == 'hospital'):
				hid = request.json['HID']
				subquery= "SELECT * FROM Hospital_Employee where UserID=%s and HID=%s"%(userId,hid)
				cur.execute(subquery)
				if(cur.fetchone() is None):
					return jsonify({'status':401,'Error': 'True','message':'User is not an existing admin of your hospital'})
				sqlFormula = "DELETE FROM Hospital_Employee WHERE UserID=%s AND HID=%s"%(userId,hid)
			
			elif(place == 'blood_bank'):
				bbid = request.json['BBID']
				subquery= "SELECT * FROM Blood_Bank_Employee where UserID=%s and BBID=%s"%(userId,bbid)
				cur.execute(subquery)
				if(cur.fetchone() is None):
					return jsonify({'status':401,'Error': 'True','message':'User is not an existing admin of your Blood Bank'})
				sqlFormula = "DELETE FROM Blood_Bank_Employee WHERE UserID=%s AND BBID=%s"%(userId,bbid)
			
			elif(place == 'donation_centers'):
				dcid = request.json['DCID']
				subquery= "SELECT * FROM Donation_Centers_Employee where UserID=%s and DCID=%s"%(userId,dcid)
				cur.execute(subquery)
				if(cur.fetchone() is None):
					return jsonify({'status':401,'Error': 'True','message':'User is not an existing admin of your Donation Center'})
				sqlFormula = "DELETE FROM Donation_Centers_Employee WHERE UserID=%s AND DCID=%s"%(userId,dcid)
			
			else:
				return  jsonify({'status':401,'Error': 'True','message':'Error In Request Params - Place is not in {hospital,blood_bank,donation_centers}'})
			
			cur.execute(sqlFormula)
			mysql.connection.commit()

			response = {'status':200,'message':'Successfully Deleted Employee'}
			return jsonify(response)
	
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/addemployee',methods = ['POST'])
def addEmp():
	userId = request.json['UserID']
	place = request.json['place']

	cur = mysql.connection.cursor()
	query = " SELECT * FROM User where UserID=%s"%(userId)

	try: 
		cur.execute(query)
		user = cur.fetchone()
		if(user is None):
			return jsonify({'status':401,'Error': 'True','message':'''UserID Doesn't Exist'''})
		elif(user['Type']=='Donor'):
			return jsonify({'status':401,'Error': 'True','message':'User is not of type Admin!'})
		else:
			
			if(place == 'hospital'):
				hid = request.json['HID']
				sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
				toPut = (userId,hid)
			
			elif(place == 'blood_bank'):
				bbid = request.json['BBID']
				sqlFormula = "INSERT INTO Blood_Bank_Employee VALUES(%s,%s)"
				toPut = (userId,bbid)

			elif(place == 'donation_centers'):
				dcid = request.json['DCID']
				sqlFormula = "INSERT INTO Donation_Centers_Employee VALUES(%s,%s)"
				toPut = (userId,dcid)

			else:
				return  jsonify({'Error': 'True','message':'Not a valid place'})
			
			cur.execute(sqlFormula,toPut)
			mysql.connection.commit()

			response = {'status':200,'message':'Successfully Added Employee!'}
			return jsonify(response)
	
	except Exception as e:
		return jsonify({'status':401,'Error': 'True','message': str(e)})


# Working / Uses Transaction
@app.route('/updateuser',methods = ['POST'])
def updateUser():

	id_ = request.json['UserID']
	user = request.json['user']
	print_it(user)

	response = ""
	
	try:
		mycursor = mysql.connection.cursor()	
		
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")
		
		#Update values in user table
		sqlFormula = "UPDATE User SET Type=%s,Username=%s,Phone=%s,Email=%s,Address=%s,Pincode=%s,Age=%s WHERE UserID=%s"
		toPut = (user["Type"],user["Username"],user["Phone"],user["Email"],user["Address"],user["Pincode"],user["Age"],id_)
		mycursor.execute(sqlFormula,toPut)


		#Update values in password table
		if (len(user["Password"]) > 0 ):
			sqlPass = "UPDATE Passwords SET Password=%s,Username=%s WHERE UserID=%s"
			toPut = (user["Password"],user["Username"],id_)
			mycursor.execute(sqlPass,toPut)
		

		#Update values in Donor table
		if(user['Type']=="Donor"):
			query = "UPDATE Available_Donor SET BloodGroup=%s,WillingToDonate=%s WHERE UserID=%s"
			toPut = (user["Bloodgroup"],user["WTD"],id_)
			mycursor.execute(query,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		#Make successful response
		response = {'userid':id_, 'status': 200, 'message':'Success'}
	
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Dropped Query
# @app.route('/getemergencyrequirements/<userId>')
# def getemergencyrequirements(userId):
# 	cur = mysql.connection.cursor()
	
# 	subquery = 'SELECT BloodGroup FROM Available_Donor where UserID=%s'%(userId)
	
# 	try: 
# 		cur.execute(subquery)
# 		bloodGroup = cur.fetchall()[0]['BloodGroup']
# 		query = 'SELECT BloodNeeded, AdmissionDate,Patients_List.HID,Name,Pincode,Address FROM Patients_List, Hospital where Patients_List.HID = Hospital.HID and Patients_List.BloodNeeded="%s"'%(bloodGroup)
# 		cur.execute(query)
# 		results = cur.fetchall()
# 		print_it(type(results))
# 		return jsonify(results)
# 	except Exception as e:
# 		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/getallhospitals')
def getallhospitals():
	cur = mysql.connection.cursor()
	query = "SELECT * FROM Hospital"
	try: 
		cur.execute(query)
		results = cur.fetchall()
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/getnearbyhospitals/<userId>')
def getnearbyhospitals(userId):
	cur = mysql.connection.cursor()
	query = "SELECT * FROM Hospital where Pincode in (Select Pincode from User where UserID=%s)"%(userId)
	try: 
		cur.execute(query)
		results = cur.fetchall()
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/getalldc')
def getalldc():
	cur = mysql.connection.cursor()
	query = "SELECT * FROM Donation_Centers"
	try: 
		cur.execute(query)
		results = cur.fetchall()
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/getnearbydc/<userId>')
def getnearbydc(userId):
	cur = mysql.connection.cursor()
	query = "SELECT * FROM Donation_Centers where Pincode in (Select Pincode from User where UserID=%s)"%(userId)

	try: 
		cur.execute(query)
		results = cur.fetchall()
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working / Uses Transaction
@app.route('/addbloodbank',methods = ['POST'])
def addBloodBank():
	name = request.json['Name']
	address = request.json['Address']
	pincode = request.json['Pincode']
	user_list = request.json['UserID']
	totalCap = request.json['TotalCapacity']
	capLeft = request.json['CapacityLeft']

	try:
		mycursor = mysql.connection.cursor()	
		# BEGIN TRANSACTION
		mycursor.execute("BEGIN")

		query = "SELECT count(*) FROM Blood_Bank"
		mycursor.execute(query)
		
		#New id as total blood_banks + 1
		id_ = mycursor.fetchall()[0]['count(*)'] + 1
		print_it(id_)
		
		sqlFormula = "INSERT INTO Blood_Bank VALUES(%s,%s,%s,%s,%s,%s)"
		toPut = (name,id_,address,pincode,capLeft,totalCap)

		mycursor.execute(sqlFormula,toPut)

		for uid in user_list:
			query = " SELECT * FROM User where UserID=%s"%(uid)
			mycursor.execute(query)
			results = mycursor.fetchall()
			if(len(results)==0):
				return jsonify({'Error': 'True','message':'No such user'+str(uid)})
			else:
				sqlFormula = "INSERT INTO Blood_Bank_Employee VALUES(%s,%s)"
				toPut = (uid,id_)
				mycursor.execute(sqlFormula,toPut)

		# If no exception, then COMMIT the transaction
		mysql.connection.commit()
		response = {'status':200,'message':'Created a new blood bank, with ID='+str(id_),'BBID':id_}
		return jsonify(response)
	except Exception as e:
		# If exception occurs, ROLLBACK!!
		mycursor.execute("ROLLBACK")
		return jsonify({'status':401,'Error': 'True','message': str(e)})


# Working
@app.route('/adddonationcenter',methods = ['POST'])
def addDonCen():
	name = request.json['Name']
	address = request.json['Address']
	pincode = request.json['Pincode']
	user_list = request.json['UserID']
	bbid = request.json['BBID']

	try:
		mycursor = mysql.connection.cursor()	
		query = "SELECT count(*) FROM Donation_Centers"
		mycursor.execute(query)
		
		#New id as total Donation_Centers + 1
		id_ = mycursor.fetchall()[0]['count(*)'] + 1
		print_it(id_)
		
		sqlFormula = "INSERT INTO Donation_Centers VALUES(%s,%s,%s,%s,%s)"
		toPut = (name,id_,address,pincode,bbid)

		mycursor.execute(sqlFormula,toPut)
		mysql.connection.commit()

		for uid in user_list:
			query = " SELECT * FROM User where UserID=%s"%(uid)
			mycursor.execute(query)
			results = mycursor.fetchall()
			if(len(results)==0):
				return jsonify({'Error': 'True','message':'No such user'+str(uid)})
			else:
				sqlFormula = "INSERT INTO Donation_Centers_Employee VALUES(%s,%s)"
				toPut = (uid,id_)
				mycursor.execute(sqlFormula,toPut)
				mysql.connection.commit()

		response = {'status':200,'message':'Created a new donation center, with ID='+str(id_),'DCID':id_}
		return jsonify(response)

	except Exception as e:
		return jsonify({'status':401,'Error': 'True','message': str(e)})


# Working
@app.route('/addhospital',methods = ['POST'])
def addHospital():
	name = request.json['Name']
	address = request.json['Address']
	pincode = request.json['Pincode']
	user_list = request.json['UserID']
	admPatient = request.json['AdmittedPatients']

	try:
		mycursor = mysql.connection.cursor()	
		query = "SELECT count(*) FROM Hospital"
		mycursor.execute(query)
		
		#New id as total Hospital + 1
		id_ = mycursor.fetchall()[0]['count(*)'] + 1
		print_it(id_)
		
		sqlFormula = "INSERT INTO Hospital VALUES(%s,%s,%s,%s,%s)"
		toPut = (id_,name,address,pincode,admPatient)
		mycursor.execute(sqlFormula,toPut)
		mysql.connection.commit()

		for uid in user_list:
			query = " SELECT * FROM User where UserID=%s"%(uid)
			mycursor.execute(query)
			results = mycursor.fetchall()
			if(len(results)==0):
				return jsonify({'Error': 'True','message':'No such user'+str(uid)})
			else:
				sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
				toPut = (uid,id_)
				mycursor.execute(sqlFormula,toPut)
				mysql.connection.commit()

		response = {'status':200,'message':'Created a new hospital, with ID='+str(id_),'HID':id_}
		return jsonify(response)

	except Exception as e:
		return jsonify({'status':401,'Error': 'True','message': str(e)})


# Working
@app.route('/donateblood',methods = ['POST'])
def donateBlood():
	userIdArray = request.json['UserID']
	AdminID = request.json['AdminID']
	dateRec = request.json['DateRecieved']
	# amt = request.json['Amount']
	try:
		cur = mysql.connection.cursor()
		sqlFormula = "INSERT INTO Donated_Blood VALUES(%s,%s,%s,%s,%s,%s)"
		i=0	
		queryGetDCID = "SELECT DCID FROM Donation_Centers_Employee where UserID=%s"%(AdminID)
		cur.execute(queryGetDCID)
		DCID = cur.fetchall()[0]['DCID']
		for user in userIdArray:
			# Check if user is donor type
			subquery = 'SELECT Type FROM user where UserID=%s'%(user)
			cur.execute(subquery)
			if(cur.fetchone()['Type']=="Donor"):
				# Get Donor Blood Group
				subquery = 'SELECT BloodGroup FROM Available_Donor where UserID=%s'%(user)
				cur.execute(subquery)
				bloodGroup = cur.fetchall()[0]['BloodGroup']
				# Add Donation Record
				toPut = (user,dateRec,bloodGroup,1,DCID,0)
				print(sqlFormula,toPut)
				cur.execute(sqlFormula,toPut)
				mysql.connection.commit()
				i=i+1
				response = {'status':200,'message':'Successfully Updated Donation Record'}
			else:
				response = {'status':401,'message':'User is not of type Donor!'}
		return jsonify(response)

	except Exception as e:
		return jsonify({'status':401,'Error': 'True','message': str(e)})

@app.route('/showprofile')
@jwt_required
def showProfile():
	UserID = get_jwt_identity()
	cur = mysql.connection.cursor()
	query = " SELECT * FROM User where UserID=%s"%(UserID)

	try: 
		cur.execute(query)
		results = cur.fetchall()[0]
		if(results['Type']=='Donor'):
			subquery = 'SELECT BloodGroup FROM Available_Donor where UserID=%s'%(UserID)
			cur.execute(subquery)
			bloodGroup = cur.fetchall()[0]
			results.update(bloodGroup)
			subquery = 'SELECT WillingToDonate FROM Available_Donor where UserID=%s'%(UserID)
			cur.execute(subquery)
			wtd = cur.fetchall()[0]
			results.update(wtd)
		if(results['Type']=='Admin'):
			queries = []
			queries.append("Create temporary table associatedOrganization(UserID int, hasBloodBank bool, hasDonationCenter bool, hasHospital bool)")
			queries.append("insert into associatedOrganization select UserID,false,false,false from User where type='Admin'")
			queries.append("update associatedOrganization set hasBloodBank=true where UserID in (select UserID from Blood_Bank_Employee)")
			queries.append("update associatedOrganization set hasDonationCenter=true where UserID in (select UserID from Donation_Centers_Employee)")
			queries.append("update associatedOrganization set hasHospital=true where UserID in (select UserID from Hospital_Employee)")
			# queries.append("delete from associatedOrganization where hasBloodBank=0 and hasDonationCenter=0 and hasHospital=0")
			queries.append("select * from associatedOrganization where UserID=%s"%(UserID))
			for query in queries:
				cur.execute(query)
			org = cur.fetchone()
			results.update(org)
			subquery="drop table associatedOrganization"
			cur.execute(subquery)
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working
@app.route('/login', methods=['POST'])
@jwt_optional
def login():
	UserID = get_jwt_identity()
	if(UserID):
		access_token = create_access_token(identity=UserID)
		return jsonify({'message':'Logged in successfully','access_token':access_token}),200
	UserID = request.json["UserID"]
	cur = mysql.connection.cursor()
	query = " SELECT * FROM Passwords where UserID=%d"%(UserID)
	try: 
		cur.execute(query)
		results = cur.fetchall()[0]
		if(results['Password']==request.json["Password"]):
			access_token = create_access_token(identity=UserID)
			return jsonify({'message':'Logged in successfully','access_token':access_token}),200
		else:
			return jsonify({'message':'Wrong Password'}), 401
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)}), 400



# Working
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

	response = ""
	
	try:
		#Insert values in user table
		sqlFormula = "INSERT INTO User VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
		toPut = (id_,user["Type"],user["Username"],user["Phone"],user["Email"],user["Address"],user["Pincode"],user["Age"])
		mycursor.execute(sqlFormula,toPut)
		mysql.connection.commit()


		#Insert values in password table
		sqlPass = "INSERT INTO Passwords VALUES(%s,%s,%s)"
		toPut = (id_,user["Password"],user["Username"])
		mycursor.execute(sqlPass,toPut)
		mysql.connection.commit()
		

		#Insert values in Donor table
		if(user['Type']=="Donor"):
			query = "INSERT into Available_donor values(%s,%s,%s,%s)"
			toPut = (id_,date.today(),user["Bloodgroup"],user["WTD"])
			mycursor.execute(query,toPut)
			mysql.connection.commit()

		#Make succesfull response
		response = {'userid':id_, 'status': 200, 'message':'Success'}
	
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})

	#Send back the response
	return jsonify(response)


# Working
@app.route('/getpastdonations/<userId>')
def getpastdonations(userId):
	cur = mysql.connection.cursor()
	query = " SELECT * FROM Donated_Blood where UserID=%s"%(userId)
	try: 
		cur.execute(query)
		results = cur.fetchall()

		for i in range(len(results)):
			donationDate = results[i]['DateRecieved']
			formattedDate = donationDate.strftime("%Y")+'-'+donationDate.strftime("%m")+'-'+donationDate.strftime("%d")
			results[i]['DateRecieved'] = formattedDate
			DCID = results[i]['DCID']
			subquery = "SELECT Name FROM Donation_Centers where DCID=%s"%(DCID)  # SUBQUERY to get Donation Center Name
			cur.execute(subquery)
			Name = cur.fetchall()[0]
			results[i].update(Name)
		print_it(type(results))
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


# Working / Uses TEMPORARY TABLE
@app.route('/getAdminOrganization/<userId>')
def getAdminOrganization(userId):
	cur = mysql.connection.cursor()
	queries = []
	queries.append("Create temporary table associatedOrganization(UserID int, BBE bool, DCE bool, HE bool)")
	queries.append("insert into associatedOrganization select UserID,false,false,false from User where type='Admin'")
	queries.append("update associatedOrganization set BBE=true where UserID in (select UserID from Blood_Bank_Employee)")
	queries.append("update associatedOrganization set DCE=true where UserID in (select UserID from Donation_Centers_Employee)")
	queries.append("update associatedOrganization set HE=true where UserID in (select UserID from Hospital_Employee)")
	queries.append("delete from associatedOrganization where BBE=0 and DCE=0 and HE=0")
	queries.append("select * from associatedOrganization where UserID=%s"%(userId))
	
	
	try: 
		for query in queries:
			cur.execute(query)
		results = cur.fetchall()[0]
		subquery="drop table associatedOrganization"
		cur.execute(subquery)
		return jsonify(results)
	except Exception as e:
		return jsonify({'Error': 'True','message': str(e)})


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
if __name__ == "__main__":
	app.run(debug=true)

#=============================================================================================#