import mysql.connector
from data import *
from random import randint
import config						#need to have secret keys in config.py

# =========================== LOCAL SQL SERVER ===========================
# host="localhost"
# user="root"
# passwd="lakshay"
# # passwd="dbms_123"
# database="ConnectGroup"


# =========================== REMOTE SQL SERVER ===========================
# host="remotemysql.com"
# user="swMUYUcOTM"
# passwd="LlyHn4U47w"
# database="swMUYUcOTM


# =========================== HEROKU APP ===========================
# For local heroku server dev

host=config.MYSQL_HOST
user=config.MYSQL_USER
passwd=config.MYSQL_PASSWORD
database=config.MYSQL_DB



# Initialise SQL Connection
mydb = mysql.connector.connect(
	host=host,
	user=user,
	passwd=passwd,
	database=database
)
mycursor=mydb.cursor()


# Start Populating

Address = ['Sukhdev Vihar', 'Okhla Phase 3', 'Okhla NSIC', 'Hauz Khas', 'Chirag Delhi', 'Safdurjang', 'Vasant Kunj']
Pincodes = ["110025","110020","110019","110016","110017","110029","110070"]
TotalCapacity = [5000,10000]

def getPincode():
	return Pincodes[randint(0,len(Pincodes)-1)]

def getRandNumber():
	return randint(0,len(Pincodes)-1)

print("Populating USER TABLE")
############ USER TABLE ############
sqlFormula = "INSERT INTO User VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
i=1
for user in Users:
	addressToss = getRandNumber()
	toPut = (i,user["Type"],user["Username"],user["Phone"],user["Email"],Address[addressToss],Pincodes[addressToss],user["Age"])
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

print("Populating HOSPITAL TABLE")
############ HOSPITAL TABLE ############
sqlFormula = "INSERT INTO Hospital VALUES(%s,%s,%s,%s,%s)"
i=1
for h in Hospitals:
	addressToss = getRandNumber()
	toPut = (i,h["Name"]+" Hospital",Address[addressToss],Pincodes[addressToss],h["AdmittedPatients"])
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

print("Populating Passwords TABLE")
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

print("Populating Blood_Bank TABLE")
############ BLOOD BANK TABLE ############
sqlFormula = "INSERT INTO Blood_Bank VALUES(%s,%s,%s,%s,%s,%s)"
i=1
for h in BloodBanks:
	# print(h)
	addressToss = getRandNumber()
	TCap = TotalCapacity[randint(0,1)]
	toPut = (h["Name"]+" Blood Bank",i,Address[addressToss],Pincodes[addressToss],TCap,TCap)
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

print("Populating Donation_Centers TABLE")
############ DONATION_CENTER TABLE ############
sqlFormula = "INSERT INTO Donation_Centers VALUES(%s,%s,%s,%s,%s)"

i=1
for h in Donation_Centers:
	# print(h)
	addressToss = getRandNumber()
	toPut = (h["Name"]+" Donation Center",i,Address[addressToss],Pincodes[addressToss],i)
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

print("Populating Donated Blood TABLE")
############ Donated Blood TABLE ############
sqlFormula = "INSERT INTO Donated_Blood VALUES(%s,%s,%s,%s,%s,%s)"
for i in range(30,60):
	h=Available_Donors[i]
	toPut = (i,h["RegisteredOn"],h["BloodGroup"],randint(1,3),randint(1,100),randint(0,1))
	# print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

print("Populating Available_Donor TABLE")
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

print("Populating Patients_List TABLE")
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

print("Populating ProfilePictures TABLE")
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

print("Populating Appointment TABLE")
############ Appointment TABLE ############
sqlFormula = "INSERT INTO Appointment VALUES(%s,%s,%s,%s)"
for i in range(1,6):
	toPut = (i,randint(1,100),randint(1,50),Patients_List[i]["AdmissionDate"])
	mycursor.execute(sqlFormula,toPut)
	mydb.commit()

print("Populating Hospital_Employee TABLE")
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

# 
sqlFormula = """Delete from available_donor where available_donor.UserID in (select UserID from user where Type="Admin")"""
mycursor.execute(sqlFormula)
mydb.commit()

# ------------------------------------- Indexes ------------------------------------- #
# UserID Indexes
sqlFormula = "CREATE INDEX idx_user_UserID ON User (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_appointment_UserID ON appointment (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_available_donor_UserID ON available_donor (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_blood_bank_employee_UserID ON blood_bank_employee (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_donated_blood_UserID ON donated_blood (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_donation_centers_employee_UserID ON donation_centers_employee (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_hospital_employee_UserID ON hospital_employee (UserID)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_passwords_UserID ON passwords (UserID)"
mycursor.execute(sqlFormula)

# Pincode Indexes
sqlFormula = "CREATE INDEX idx_user_Pincode ON User (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_donation_centers_Pincode ON Donation_Centers (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_hospital_Pincode ON Hospital (Pincode)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_blood_bank_Pincode ON Blood_Bank (Pincode)"
mycursor.execute(sqlFormula)
mydb.commit()

# Blood Group Indexes
sqlFormula = "CREATE INDEX idx_donated_blood_BG ON Donated_Blood (BloodGroup)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_available_donor_BG ON Available_Donor (BloodGroup)"
mycursor.execute(sqlFormula)
sqlFormula = "CREATE INDEX idx_patients_list_BG ON Patients_List (BloodNeeded)"
mycursor.execute(sqlFormula)
mydb.commit()
