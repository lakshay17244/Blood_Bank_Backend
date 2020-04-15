import mysql.connector
from data import *
from random import randint

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="dbms_123",
	database="ConnectGroup"
)

mycursor=mydb.cursor()


############ USER TABLE ############
sqlFormula = "INSERT INTO user VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
i=1
for user in Users:
	
	toPut = (i,user["Type"],user["Username"],user["Phone"],user["Email"],user["Address"],user["Pincode"],user["Age"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ HOSPITAL TABLE ############
sqlFormula = "INSERT INTO hospital VALUES(%s,%s,%s,%s,%s)"
i=1
for h in Hospitals:
	# print(h)
	toPut = (i,h["Name"]+" Hospital",h["Pincode"],h["Address"],h["AdmittedPatients"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ PASSWORDS TABLE ############
sqlFormula = "INSERT INTO passwords VALUES(%s,%s,%s)"
i=1
for passwd in Passwords:
	# print(passwd)
	toPut = (i,passwd["Password"],Users[i-1]["Username"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ BLOOD BANK TABLE ############
sqlFormula = "INSERT INTO Blood_Bank VALUES(%s,%s,%s)"
i=1
for h in BloodBanks:
	# print(h)
	toPut = (i,randint(0,h["TotalCapacity"]),h["TotalCapacity"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ DONATION_CENTER TABLE ############
sqlFormula = "INSERT INTO Donation_Centers VALUES(%s,%s,%s,%s)"

i=1
for h in Donation_Centers:
	# print(h)
	toPut = (i,h["Pincode"],h["Address"],i)
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

############ Donated Blood TABLE ############
sqlFormula = "INSERT INTO Donated_Blood VALUES(%s,%s,%s,%s,%s,%s)"
for i in range(30,60):
	h=Available_Donors[i]
	toPut = (i,h["RegisteredOn"],h["BloodGroup"],randint(1,3),randint(1,100),randint(0,1))
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

########### Available Donors TABLE ############
sqlFormula = "INSERT INTO Available_Donor VALUES(%s,%s,%s,%s)"
i=1
for h in Available_Donors:
	# print(h)
	toPut = (i,h["RegisteredOn"],h["BloodGroup"],h["WillingToDonate"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()

########### Patients List TABLE ############
sqlFormula = "INSERT INTO Patients_List VALUES(%s,%s,%s,%s)"

for h in Patients_List:
	# print(h)
	toPut = (h["UserID"],h["AdmissionDate"],h["BloodNeeded"],h["HID"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	mydb.commit()

############ Profile Pictures TABLE ############
sqlFormula = "INSERT INTO Profile_Picture VALUES(%s,%s)"
i=1
for h in ProfilePictures:
	# print(h)
	toPut = (i,h["URL"])
	print(toPut)
	mycursor.execute(sqlFormula,toPut)
	i=i+1
	mydb.commit()


############ Hospital_Employee TABLE ############

sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
for i in range(1,100):
	h=Users[i]
	if(h["Type"]=="Admin"):
		toPut = (i,randint(1,100))
		print(toPut)
		toss = randint(0,3)
		if(toss==0):
			sqlFormula = "INSERT INTO Hospital_Employee VALUES(%s,%s)"
		elif(toss==1):
			sqlFormula = "INSERT INTO Blood_Bank_Employee VALUES(%s,%s)"
		else:
			sqlFormula = "INSERT INTO Donation_Centers_Employee VALUES(%s,%s)"
		
		mycursor.execute(sqlFormula,toPut)
		mydb.commit()
