# ANPR Software for MSc Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# Import Libraries and Dependencies
import csv
import sqlite3

# Script responsible for initialising the database with specified columns

def setupDB():
    conn = sqlite3.connect('vehicleData.db')    # Connect to database
    cursor = conn.cursor()

    # Creation of table for AUTHORISED PLATES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platesAuthorised (
            PLATE TEXT PRIMARY KEY,
            FORENAME TEXT,
            SURNAME TEXT,
            TYPE TEXT,
            DATE_ADDED DATE,
            VEHICLE_MAKE TEXT,
            VEHICLE_COLOUR TEXT
        )
    ''')

    # Creation of tabel for DETECTED PLATES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platesDetected (
            PLATE TEXT PRIMARY KEY,
            VEHICLE_ID INTEGER
        )
    ''')

    # Commit changes and terminate database connection
    conn.commit()
    conn.close()

def populateDetectedPlatesTable(csvFilePath):
    conn = sqlite3.connect('vehicleData.db')   # Establish Connection
    cursor = conn.cursor()

    # Clear table first
    clearPlatesDetected('platesDetected')

    # Examine CSV data
    with open(csvFilePath, 'r') as file:
        reader = csv.reader(file)
        next(reader)    # Dismisses header row

        # Populate DETECTED PLATES table
        for row in reader:
            Vehicle_ID, NumPlate = row
            cursor.execute(
                'INSERT OR IGNORE INTO platesDetected (VEHICLE_ID, PLATE) VALUES (?, ?)',
                (Vehicle_ID, NumPlate))

    # Commit changes and terminate connection
    conn.commit()
    conn.close()

def populateAuthorisedPlatesTable(csvFilePath):
    conn = sqlite3.connect('vehicleData.db')   # Establish Connection
    cursor = conn.cursor()

    # Examine CSV data
    with open(csvFilePath, 'r') as file:
        reader = csv.reader(file)
        next(reader)    # Dismisses header row

        # Populate AUTHORISED PLATES table
        for row in reader:
            plate, forename, surname, type, date_added, vehicle_make, vehicle_colour = row
            cursor.execute('INSERT OR IGNORE INTO platesAuthorised (PLATE, FORENAME, SURNAME, TYPE, DATE_ADDED, VEHICLE_MAKE, VEHICLE_COLOUR) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (plate, forename, surname, type, date_added, vehicle_make, vehicle_colour))

    # Commit changes and terminate connection
    conn.commit()
    conn.close()

def generateReport():
    conn = sqlite3.connect('vehicleData.db')  # Establish Connection
    cursor = conn.cursor()

    # Fetch exact values for DETECTED PLATES
    cursor.execute("SELECT PLATE FROM platesDetected")
    detectedPlates = cursor.fetchall()

    # Fetch exact values for AUTHORISED PLATES
    cursor.execute("SELECT PLATE FROM platesAuthorised")
    authorisedPlates = set(entry[0] for entry in cursor.fetchall())

    # Identify unrecognised plates
    unidentifiedPlates = [plate[0] for plate in detectedPlates if plate[0] not in authorisedPlates]

    # Generate Report

    reportList = []

    if unidentifiedPlates:
        print("Unidentified Vehicles Recorded:")
        for plate in unidentifiedPlates:
            print(f"{plate} is an unidentified vehicle")
            reportList.append(f"{plate} is an unidentified vehicle")
    else:
        print("0 unidentified vehicles found.")
        reportList.append("0 unidentified vehicles found.")

    return reportList

    # Terminate database connection
    conn.close()


def clearPlatesDetected(tableName):
    conn = sqlite3.connect('vehicleData.db')   # Establish Connection
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {tableName}")

    # Commit changes and terminate connection
    conn.commit()
    conn.close()

def clearCSVFile(filePath):
    with open(filePath, 'w') as file:
        file.truncate(0)

setupDB()
populateDetectedPlatesTable('/Users/emanbegah/Desktop/ANPR/Dev/realRecords.csv')
populateAuthorisedPlatesTable('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/platesAuthorised.csv')
