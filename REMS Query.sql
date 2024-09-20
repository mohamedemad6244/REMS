CREATE DATABASE REMS;

USE REMS;

-- Lookup tables
CREATE TABLE PropertyTypes (
    TypeID INT PRIMARY KEY IDENTITY(1,1),
    TypeName VARCHAR(100) NOT NULL UNIQUE  -- Adjusted TypeName length
);

CREATE TABLE Features (
    FeatureID INT PRIMARY KEY IDENTITY(1,1),
    FeatureName VARCHAR(100) NOT NULL UNIQUE  -- Adjusted FeatureName length
);

-- Main tables
CREATE TABLE Properties (
    Property_ID INT PRIMARY KEY IDENTITY(1,1),
    TypeID INT NOT NULL,
    Size INTEGER NOT NULL,
    Price INT NOT NULL CHECK(Price >= 0),
    Current_Status VARCHAR(20) NOT NULL CHECK(Current_Status IN ('Sold', 'For Rent', 'For Sale', 'Not Available')),
    City VARCHAR(100) NOT NULL,  -- Adjusted City length
    Address_Line1 VARCHAR(100) NOT NULL,  -- Adjusted Address length
    Address_Line2 VARCHAR(100),  -- Adjusted Address length
    State VARCHAR(100),  -- Adjusted State length
    Bathrooms_No INT CHECK(Bathrooms_No >= 0),
    Bedrooms_No INT CHECK(Bedrooms_No >= 0),
    FeatureID INT,
    Furniture INT NOT NULL CHECK(Furniture IN (0, 1)),
    Listing_Date DATE NOT NULL,  -- Changed Listing_Date to DATE type
    Note VARCHAR(MAX),  -- Adjusted Note to MAX length
    Owner_ID INT,
    FOREIGN KEY (TypeID) REFERENCES PropertyTypes(TypeID),
    FOREIGN KEY (FeatureID) REFERENCES Features(FeatureID),
    FOREIGN KEY (Owner_ID) REFERENCES Customers(Customer_ID)
);

alter table Properties
add Original_Status varchar


CREATE TABLE Agents (
    Agent_ID INT PRIMARY KEY IDENTITY(1,1),
    F_Name VARCHAR(100) NOT NULL,  -- Adjusted F_Name length
    L_Name VARCHAR(100) NOT NULL,  -- Adjusted L_Name length
    Email_Address VARCHAR(100) UNIQUE,  -- Adjusted Email_Address length
    Phone_No VARCHAR(20),  -- Adjusted Phone_No length
    Date_Hired DATE NOT NULL,  -- Changed Date_Hired to DATE type
    License_Number VARCHAR(20) NOT NULL UNIQUE  -- Adjusted License_Number length
);

CREATE TABLE Customers (
    Customer_ID INT PRIMARY KEY IDENTITY(1,1),
    F_Name VARCHAR(100) NOT NULL,  -- Adjusted F_Name length
    L_Name VARCHAR(100) NOT NULL,  -- Adjusted L_Name length
    Phone VARCHAR(20),  -- Adjusted Phone length
    Email VARCHAR(100) UNIQUE,  -- Adjusted Email length
    Customer_City VARCHAR(100)  -- Adjusted Customer_City length
);

CREATE TABLE Deals (
    Deal_ID INT PRIMARY KEY IDENTITY(1,1),  -- Removed AUTOINCREMENT for SQL Server
    Deal_Status VARCHAR(20) CHECK (Deal_Status IN ('Pending', 'Completed', 'Cancelled')),
    Act_End_Date DATE,  -- Changed Act_End_Date to DATE type
    Property_ID INT,
    Customer_ID INT,
    Agent_ID INT,
    Deal_Type VARCHAR(20) CHECK (Deal_Type IN ('Cash', 'Installment', 'Renting')),
    Note VARCHAR(MAX),  -- Adjusted Note to MAX length
    FOREIGN KEY (Property_ID) REFERENCES Properties (Property_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customers (Customer_ID),
    FOREIGN KEY (Agent_ID) REFERENCES Agents (Agent_ID)
);



CREATE TABLE Cash_Deals (
    Cash_Deal_ID INT PRIMARY KEY,  -- Removed AUTOINCREMENT for SQL Server
    Deal_ID INT,
    Deal_Price INT,
    Deal_Date DATE,  -- Changed Deal_Date to DATE type
    Upfront_Deposit INT,
    FOREIGN KEY (Deal_ID) REFERENCES Deals (Deal_ID)
);

CREATE TABLE Renting_Deals (
    Renting_Deal_ID INT PRIMARY KEY,  -- Removed AUTOINCREMENT for SQL Server
    Deal_ID INT,
    Rent_Start_Date DATE,  -- Changed Rent_Start_Date to DATE type
    Rent_End_Date DATE,  -- Changed Rent_End_Date to DATE type
    Monthly_Rent INT,
    Security_Deposit INT,
    FOREIGN KEY (Deal_ID) REFERENCES Deals (Deal_ID)
);

CREATE TABLE Installment_Deals (
    Installment_Deal_ID INT PRIMARY KEY,  -- Removed AUTOINCREMENT for SQL Server
    Deal_ID INT,
    Inst_Start_Date DATE,  -- Changed Inst_Start_Date to DATE type
    Inst_End_Date DATE,  -- Changed Inst_End_Date to DATE type
    Total_Price INT,
    Down_Payment INT,
    Frequency VARCHAR(100),  -- Adjusted Frequency length
    Installment_Amount INT,
    FOREIGN KEY (Deal_ID) REFERENCES Deals (Deal_ID)
);


alter table Installment_Deals
add Deal_Status varchar

alter table Cash_Deals
add Deal_Status varchar

alter table Renting_Deals
add Deal_Status varchar


-- Triggers

-- Trigger to update property status based on deal status

CREATE TRIGGER UpdatePropertyStatus
ON Deals
AFTER UPDATE
AS
BEGIN
    UPDATE Properties
    SET Current_Status = CASE
        WHEN INSERTED.Deal_Status = 'Completed' AND (INSERTED.Deal_Type = 'Cash' OR INSERTED.Deal_Type = 'Installment') THEN 'Sold'
        WHEN INSERTED.Deal_Status = 'Cancelled' THEN 'For Sale'
        WHEN INSERTED.Deal_Status = 'Pending' THEN 'Not Available'
    END
    FROM Properties
    INNER JOIN INSERTED ON Properties.Property_ID = INSERTED.Property_ID;
END;
GO






/****** Object:  Trigger [dbo].[StoreOriginalStatus]    Script Date: 8/14/2024 8:45:41 PM ******/
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER TRIGGER [dbo].[StoreOriginalStatus]
ON [dbo].[Deals]
AFTER INSERT
AS
BEGIN
    UPDATE Properties
    SET Original_Status = Current_Status
    FROM Properties
    INNER JOIN INSERTED ON Properties.Property_ID = INSERTED.Property_ID
    WHERE INSERTED.Deal_Status = 'Pending';
END;
















GO
/****** Object:  Trigger [dbo].[UpdatePropertyStatusAndOwner]    Script Date: 8/14/2024 8:48:04 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER TRIGGER [dbo].[UpdatePropertyStatusAndOwner]
ON [dbo].[Deals]
AFTER UPDATE
AS
BEGIN
    -- Handling completed deals (Cash, Installment, Renting)
    UPDATE Properties
    SET Current_Status = CASE
                            WHEN INSERTED.Deal_Status = 'Completed' AND INSERTED.Deal_Type IN ('Cash', 'Installment') THEN 'Sold'
                            WHEN INSERTED.Deal_Status = 'Completed' AND INSERTED.Deal_Type = 'Renting' THEN 'Rented'
                            ELSE Properties.Current_Status -- Maintain the current status if no condition is met
                         END,
        Owner_ID = CASE
                    WHEN INSERTED.Deal_Status = 'Completed' AND INSERTED.Deal_Type IN ('Cash', 'Installment') THEN INSERTED.Customer_ID
                    WHEN INSERTED.Deal_Status = 'Completed' AND INSERTED.Deal_Type = 'Renting' THEN Properties.Owner_ID  -- Owner remains the same for renting
                    ELSE Properties.Owner_ID -- Maintain the current owner if no condition is met
                   END
    FROM Properties
    INNER JOIN INSERTED ON Properties.Property_ID = INSERTED.Property_ID;

    -- Handling cancelled deals
    UPDATE Properties
    SET Current_Status = CASE 
                            WHEN INSERTED.Deal_Status = 'Cancelled' THEN 
                                (SELECT Original_Status FROM Properties WHERE Property_ID = INSERTED.Property_ID) 
                            ELSE Properties.Current_Status -- Maintain the current status if no condition is met
                         END
    FROM Properties
    INNER JOIN INSERTED ON Properties.Property_ID = INSERTED.Property_ID;

    -- Handling pending deals
    UPDATE Properties
    SET Current_Status = CASE 
                            WHEN INSERTED.Deal_Status = 'Pending' THEN 'Not Available'
                            ELSE Properties.Current_Status -- Maintain the current status if no condition is met
                         END
    FROM Properties
    INNER JOIN INSERTED ON Properties.Property_ID = INSERTED.Property_ID;
END;




































-- Insert example data into lookup tables
INSERT INTO PropertyTypes (TypeName) VALUES ('Flat'), ('Villa'), ('Land'), ('Factory');
INSERT INTO Features (FeatureName) VALUES ('No Finishing'), ('Half Finishing'), ('Full Finishing'), ('Lux'), ('Super Lux'), ('Ultra Lux'), ('Deluxe');

-- Insert example data into main tables
INSERT INTO Customers (F_Name, L_Name, Phone, Email, Customer_City) VALUES 
('Mohamed', 'Ahmed', '01212647632', 'mohamed.ahmed412@gmail.com', 'El Shrouk'),
('Ali', 'Khaled', '01017127236', 'ali.khaled123@gmail.com', 'El Obour'),
('Alaa', 'Younis', '01110231253', 'alaa.younis32@gmail.com', 'El Zamalek');

INSERT INTO Agents (F_Name, L_Name, Email_Address, Phone_No, Date_Hired, License_Number) VALUES 
('Khaled', 'Hosam', 'hossam91@gmail.com', '01001234567', '2022-01-15', '1234-5678-9101'),
('Ahmed', 'Ismail', 'a.ismail@gmail.com', '01222345678', '2023-07-08', '2345-6789-0123'),
('Donia', 'Fahmy', 'donia99@outlook.com', '01013456789', '2023-10-30', '3456-7890-1234');

INSERT INTO Properties (TypeID, Size, Price, Current_Status, City, Address_Line1, Address_Line2, State, Bathrooms_No, Bedrooms_No, FeatureID, Furniture, Listing_Date, Note, Owner_ID) VALUES 
(1, 190, 1000000, 'Sold', 'El Shrouk', 'Shrouk 3', NULL, NULL, 1, 2, 3, 0, '2024-01-01', 'Have finishing', 1),
(2, 600, 8600000, 'For Rent', 'Madinity', 'Madinty', NULL, NULL, 3, 4, 5, 1, '2024-01-01', 'Super deluxe finishing', 2),
(3, 2000, 30000000, 'For Sale', '10th of Ramadan', 'The 5th Settlement', NULL, NULL, NULL, NULL, 1, 0, '2024-01-01', 'Unfinished', 3);

-- Insert example data into deals table
INSERT INTO Deals (Deal_Status, Act_End_Date, Property_ID, Customer_ID, Agent_ID, Deal_Type, Note) VALUES 
('Pending', '2024-07-28', 1, 1, 1, 'Cash', 'Initial cash deal for property');

-- Get last inserted row ID for Deal_ID and insert into Cash_Deals table
DECLARE @LastDealID INT;
SET @LastDealID = SCOPE_IDENTITY();

INSERT INTO Cash_Deals (Cash_Deal_ID, Deal_ID, Deal_Price, Deal_Date, Upfront_Deposit)
VALUES (@LastDealID, @LastDealID, 1000000, '2024-07-28', 500000);
