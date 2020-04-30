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



query = []

query.append("drop database "+database)
query.append("create database "+database)
query.append("use "+database)

query.append("""CREATE TABLE `User`
( 
 `UserID`  	int UNIQUE,
 `Type`     varchar(10) ,
 `Username` varchar(30) NOT NULL ,
 `Phone`    varchar(15) NOT NULL ,
 `Email`    varchar(150) NOT NULL ,
 `Address`  varchar(60) NOT NULL ,
 `Pincode`  varchar(15) NOT NULL ,
 `Age`		int ,

PRIMARY KEY (`UserID`) ,
CHECK (`Age`>=18 or `Type`='Patient') ,
CHECK (`Type` IN ('Donor' , 'Patient','Admin'))
)""")


query.append("""CREATE TABLE `Blood_Bank`
(
 `Name`          varchar(150) NOT NULL ,
 `Pincode` 		varchar(50) NOT NULL ,
 `BBID`          int UNIQUE ,
 `Address` 		varchar(60) NOT NULL ,
 `CapacityLeft`  int NOT NULL ,
 `TotalCapacity` int ,

PRIMARY KEY (`BBID`) ,
CHECK (`TotalCapacity` BETWEEN 1 and 10000),
CHECK (`CapacityLeft` <= `TotalCapacity`)
)""")


query.append("""CREATE TABLE `Donation_Centers`
(
 `Name`         varchar(150) NOT NULL ,
 `DCID`    		int UNIQUE,
 `Pincode` 		varchar(50) NOT NULL ,
 `Address` 		varchar(60) NOT NULL ,
 `BBID`  		int NOT NULL ,


PRIMARY KEY (`DCID`) ,
FOREIGN KEY (`BBID`) REFERENCES Blood_Bank(`BBID`)
)""")


query.append("""CREATE TABLE `Available_Donor`
( 
 `UserID`  			int UNIQUE,
 `RegisteredOn`    	date NOT NULL ,
 `BloodGroup`      	varchar(3) ,
 `WillingToDonate` 	boolean DEFAULT true,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
CHECK (`BloodGroup` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
)""")


query.append("""CREATE TABLE `Donated_Blood`
(
 `UserID`  		int NOT NULL ,
 `DateRecieved` date NOT NULL ,
 `BloodGroup`   varchar(3) ,
 `Amount`       int DEFAULT 1,
 `DCID`  		int NOT NULL ,
 `Available`    int DEFAULT 0 ,

PRIMARY KEY (`UserID`, `DateRecieved`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`DCID`) REFERENCES Donation_Centers(`DCID`) ,
CHECK (`BloodGroup` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
)""")


query.append("""CREATE TABLE `Appointment`
( 
 `AID`  	int UNIQUE,
 `UserID`  		int NOT NULL ,
 `DCID`  	int NOT NULL ,
 `Date` 	date NOT NULL ,

PRIMARY KEY (`AID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`DCID`) REFERENCES Donation_Centers(`DCID`)
)""")


query.append("""CREATE TABLE `Hospital`
(
 `HID`              int UNIQUE,
 `Name`             varchar(150) NOT NULL ,
 `Pincode`          varchar(15) NOT NULL ,
 `Address`          varchar(60) NOT NULL ,
 `AdmittedPatients` int NOT NULL ,

PRIMARY KEY (`HID`)
)""")

query.append("""CREATE TABLE `EmergencyRequirements`
(
 `EID`              int UNIQUE,
 `BloodNeeded`   varchar(3) ,
 `DoctorID`  	int NOT NULL,
 `DateRecieved` date NOT NULL,
FOREIGN KEY (`DoctorID`) REFERENCES User(`UserID`),
CHECK (`BloodNeeded` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+')),
PRIMARY KEY (`EID`)
)""")


query.append("""CREATE TABLE `Patients_List`
(
 `PID` int NOT NULL,
 `UserID`  	int NOT NULL,
 `AdmissionDate` date NOT NULL,
 `BloodNeeded`   varchar(3) ,
  `HID`  	int NOT NULL,

PRIMARY KEY (`PID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`),
FOREIGN KEY (`HID`) REFERENCES Hospital(`HID`),
CHECK (`BloodNeeded` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
)""")


query.append("""CREATE TABLE `Hospital_Employee`
(
 `UserID`  	int UNIQUE,
 `HID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`HID`) REFERENCES Hospital(`HID`)
)""")


query.append("""CREATE TABLE `Blood_Bank_Employee`
(
 `UserID`  	int UNIQUE,
 `BBID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`BBID`) REFERENCES Blood_Bank(`BBID`)
)""")


query.append("""CREATE TABLE `Donation_Centers_Employee`
(
 `UserID`  	int UNIQUE,
 `DCID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`DCID`) REFERENCES Donation_Centers(`DCID`)
)""")


query.append("""CREATE TABLE `Passwords`
(
 `UserID`  	int UNIQUE,
 `Password` varchar(45) NOT NULL ,
 `Username` varchar(30) NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`)
)""")


query.append("""CREATE TABLE `Profile_Picture`
(
 `UserID`  	int UNIQUE,
 `URL`    	varchar(200) NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`)
)""")


for q in query:
    mycursor.execute(q)
mydb.commit()