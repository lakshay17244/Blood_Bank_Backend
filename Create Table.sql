create database ConnectGroup;
use ConnectGroup;


CREATE TABLE `User`
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
);


CREATE TABLE `Blood_Bank`
(
 `Name`          varchar(150) NOT NULL ,
 `Pincode` 		varchar(50) NOT NULL ,
 `Address` 		varchar(60) NOT NULL ,
 `BBID`          int UNIQUE ,
 `CapacityLeft`  int NOT NULL ,
 `TotalCapacity` int ,

PRIMARY KEY (`BBID`) ,
CHECK (`TotalCapacity` BETWEEN 1 and 10000),
CHECK (`CapacityLeft` <= `TotalCapacity`)
);


CREATE TABLE `Donation_Centers`
(
 `Name`         varchar(150) NOT NULL ,
 `DCID`    		int UNIQUE,
 `Pincode` 		varchar(50) NOT NULL ,
 `Address` 		varchar(60) NOT NULL ,
 `BBID`  		int NOT NULL UNIQUE ,


PRIMARY KEY (`DCID`) ,
FOREIGN KEY (`BBID`) REFERENCES Blood_Bank(`BBID`)
);


CREATE TABLE `Available_Donor`
( 
 `UserID`  			int UNIQUE,
 `RegisteredOn`    	date NOT NULL ,
 `BloodGroup`      	varchar(3) ,
 `WillingToDonate` 	boolean DEFAULT true,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
CHECK (`BloodGroup` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
);


CREATE TABLE `Donated_Blood`
(
 `UserID`  		int NOT NULL ,
 `DateRecieved` date NOT NULL ,
 `BloodGroup`   varchar(3) ,
 `Amount`       int DEFAULT 1,
 `DCID`  		int NOT NULL ,
 `Available`    boolean DEFAULT true ,

PRIMARY KEY (`UserID`, `DateRecieved`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`DCID`) REFERENCES Donation_Centers(`DCID`) ,
CHECK (`BloodGroup` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
);


CREATE TABLE `Hospital`
(
 `HID`              int UNIQUE,
 `Name`             varchar(150) NOT NULL ,
 `Pincode`          varchar(15) NOT NULL ,
 `Address`          varchar(60) NOT NULL ,
 `AdmittedPatients` int NOT NULL ,

PRIMARY KEY (`HID`)
);


CREATE TABLE `Patients_List`
(
 `UserID`  	int NOT NULL,
 `AdmissionDate` date NOT NULL,
 `BloodNeeded`   varchar(3) ,
  `HID`  	int NOT NULL UNIQUE,

PRIMARY KEY (`UserID`, `AdmissionDate`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`),
FOREIGN KEY (`HID`) REFERENCES Hospital(`HID`),
CHECK (`BloodNeeded` IN ('A-', 'B-', 'AB-', 'O-', 'A+', 'B+', 'AB+', 'O+'))
);


CREATE TABLE `Hospital_Employee`
(
 `UserID`  	int UNIQUE,
 `HID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`HID`) REFERENCES Hospital(`HID`)
);


CREATE TABLE `Blood_Bank_Employee`
(
 `UserID`  	int UNIQUE,
 `BBID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`BBID`) REFERENCES Blood_Bank(`BBID`)
);


CREATE TABLE `Donation_Centers_Employee`
(
 `UserID`  	int UNIQUE,
 `DCID`    	int NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`) ,
FOREIGN KEY (`DCID`) REFERENCES Donation_Centers(`DCID`)
);


CREATE TABLE `Passwords`
(
 `UserID`  	int UNIQUE,
 `Password` varchar(45) NOT NULL ,
 `Username` varchar(30) NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`)
);


CREATE TABLE `Profile_Picture`
(
 `UserID`  	int UNIQUE,
 `URL`    	varchar(200) NOT NULL ,

PRIMARY KEY (`UserID`) ,
FOREIGN KEY (`UserID`) REFERENCES User(`UserID`)
);