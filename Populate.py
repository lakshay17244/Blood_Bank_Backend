import mysql.connector
from data import *
from random import randint
import config						#need to have secret keys in config.py

# =========================== LOCAL SQL SERVER ===========================
host="localhost"
user="root"
passwd="lakshay"
# passwd="dbms_123"
database="ConnectGroup"


# =========================== REMOTE SQL SERVER ===========================
# host="remotemysql.com"
# user="swMUYUcOTM"
# passwd="LlyHn4U47w"
# database="swMUYUcOTM


# =========================== HEROKU APP ===========================
# For local heroku server dev

# host=config.MYSQL_HOST
# user=config.MYSQL_USER
# passwd=config.MYSQL_PASSWORD
# database=config.MYSQL_DB



# Initialise SQL Connection
mydb = mysql.connector.connect(
	host=host,
	user=user,
	passwd=passwd,
	database=database
)
mycursor=mydb.cursor()


# Start Populating


Pincodes = ["110010","110020","110030","110040","110050","110060","110070","110090","118900","100200"]
TotalCapacity = [5000,10000]

def getPincode():
	return Pincodes[randint(0,9)]


############ USER TABLE ############
sqlFormula = "INSERT INTO User VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
i=1
for user in Users:
	toPut = (i,user["Type"],user["Username"],user["Phone"],user["Email"],user["Address"],getPincode(),user["Age"])
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ HOSPITAL TABLE ############
sqlFormula = "INSERT INTO Hospital VALUES(%s,%s,%s,%s,%s)"
i=1
for h in Hospitals:
	# print(h)
	toPut = (i,h["Name"]+" Hospital",getPincode(),h["Address"],h["AdmittedPatients"])
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ PASSWORDS TABLE ############
sqlFormula = "INSERT INTO Passwords VALUES(%s,%s,%s)"
i=1
for passwd in Passwords:
	# print(passwd)
	toPut = (i,passwd["Password"],Users[i-1]["Username"])
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ BLOOD BANK TABLE ############
sqlFormula = "INSERT INTO Blood_Bank VALUES(%s,%s,%s,%s,%s,%s)"
i=1
for h in BloodBanks:
	# print(h)
	TCap = TotalCapacity[randint(0,1)]
	toPut = (h["Name"]+" Blood Bank",getPincode(),i,h["Address"],randint(0,TCap),TCap)
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ DONATION_CENTER TABLE ############
sqlFormula = "INSERT INTO Donation_Centers VALUES(%s,%s,%s,%s,%s)"

i=1
for h in Donation_Centers:
	# print(h)
	toPut = (h["Name"]+" Donation Center",i,getPincode(),h["Address"],i)
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ Donated Blood TABLE ############
sqlFormula = "INSERT INTO Donated_Blood VALUES(%s,%s,%s,%s,%s,%s)"
for i in range(30,60):
	h=Available_Donors[i]
	toPut = (i,h["RegisteredOn"],h["BloodGroup"],randint(1,3),randint(1,100),randint(0,1))
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

########### Available Donors TABLE ############
sqlFormula = "INSERT INTO Available_Donor VALUES(%s,%s,%s,%s)"
i=1
for h in Available_Donors:
	# print(h)
	toPut = (i,h["RegisteredOn"],h["BloodGroup"],h["WillingToDonate"])
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

########### Patients List TABLE ############
sqlFormula = "INSERT INTO Patients_List VALUES(%s,%s,%s,%s,%s)"
i=1
for h in Patients_List:
	# print(h)
	toPut = (i,h["UserID"],h["AdmissionDate"],h["BloodNeeded"],h["HID"])
	# print(toPut)
	i+=1
	mycursor.execute(sqlFormula,toPut)
	mydb.commit()

############ Profile Pictures TABLE ############
sqlFormula = "INSERT INTO Profile_Picture VALUES(%s,%s)"
i=1
for h in ProfilePictures:
	# print(h)
	toPut = (i,h["URL"])
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()


############ Appointment TABLE ############
sqlFormula = "INSERT INTO Appointment VALUES(%s,%s,%s,%s)"
for i in range(1,6):
	toPut = (i,randint(1,100),randint(1,50),Patients_List[i]["AdmissionDate"])
	mycursor.execute(sqlFormula,toPut)
	mydb.commit()


############ Hospital_Employee TABLE ############

sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
for i in range(1,100):
	h=Users[i]
	if(h["Type"]=="Admin"):
		toPut = (i,randint(1,100))
		# print(toPut)
		toss = randint(0,3)
		if(toss==0):
			sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
		elif(toss==1):
			sqlFormula = "INSERT INTO Blood_Bank_Employee VALUES(%s,%s)"
		else:
			sqlFormula = "INSERT INTO Donation_Centers_Employee VALUES(%s,%s)"
		
		mycursor.execute(sqlFormula,toPut)
		mydb.commit()


# Delete Donor Type Associated with Blood Bank
sqlFormula = """Delete FROM Blood_Bank_Employee where UserID in (Select UserID from User where type="Donor")"""
mycursor.execute(sqlFormula)
mydb.commit()

# Delete Donor Type Associated with Hospital
sqlFormula = """Delete FROM Hospital_Employee where UserID in (Select UserID from User where type="Donor")"""
mycursor.execute(sqlFormula)
mydb.commit()

# Delete Donor Type Associated with Donation Center
sqlFormula = """Delete FROM Donation_Centers_Employee where UserID in (Select UserID from User where type="Donor")"""
mycursor.execute(sqlFormula)
mydb.commit()



# ------------------------------------- Indexes ------------------------------------- #

# Pincode
sqlFormula = "CREATE INDEX idx_user_Pincode ON User (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_donation_centers_Pincode ON Donation_Centers (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_hospital_Pincode ON Hospital (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_blood_bank_Pincode ON Blood_Bank (Pincode)"
mycursor.execute(sqlFormula)
mydb.commit()

# Blood Group
sqlFormula = "CREATE INDEX idx_donated_blood_BG ON Donated_Blood (BloodGroup)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_available_donor_BG ON Available_Donor (BloodGroup)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_patients_list_BG ON Patients_List (BloodNeeded)"
mycursor.execute(sqlFormula)
mydb.commit()
