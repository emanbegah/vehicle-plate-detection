# ANPR Software for M.Sc. Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# File stores routes that user can navigate to

# Import Libraries
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
import datetime
import json

from DatabaseModel.configDB import generateReport
from videoDetect import videoDetection

view = Blueprint('view', __name__)


@view.route('/index')
@login_required
def index():
    # Establish database connection
    conn = sqlite3.connect('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/vehicleData.db')
    cursor = conn.cursor()

    # Fetch data from platesAuthorised table
    cursor.execute("SELECT * FROM platesAuthorised")
    data = cursor.fetchall()

    # Terminate connection
    conn.close()

    return render_template("index.html", user=current_user, data=data)


@view.route('/register-vehicle', methods=['GET', 'POST'])
def registerVehicle():
    if request.method == 'POST':
        # Retrieve data from the form
        plate = request.form.get('plate')
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        type = request.form.get('type')
        vehicleMake = request.form.get('vehicle-make')
        vehicleColour = request.form.get('vehicle-colour')

        # Obtain current date and time
        currentDate = datetime.datetime.now()

        # Format to DD/MM/YYYY
        dateAdded = currentDate.strftime('%d/%m/%Y')

        # Establish database connection
        conn = sqlite3.connect('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/vehicleData.db')
        cursor = conn.cursor()

        # Write data to platesAuthorised table
        cursor.execute("INSERT INTO platesAuthorised (plate, forename, surname, type, date_added, vehicle_make, vehicle_colour) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (plate, forename, surname, type, dateAdded, vehicleMake, vehicleColour))

        # Commit changes and terminate database connection
        conn.commit()
        conn.close()

        # Redirect user to vehicle database page with updated data
        flash('Vehicle Authorised', category='success')
        return redirect(url_for('view.index'))

    # If GET request, display form
    return render_template('register-vehicle.html', user=current_user)


@view.route('/remove-vehicle', methods=['POST'])
def removeVehicle():
    data = json.loads(request.data)
    selectedPlates = data.get('selectedPlates')

    # Establish database connection
    conn = sqlite3.connect('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/vehicleData.db')
    cursor = conn.cursor()

    # Placeholders required for IN clause usage
    placeholders = ', '.join(['?' for _ in selectedPlates])

    # Delete specified entry
    cursor.execute("DELETE FROM platesAuthorised WHERE PLATE IN ({})".format(placeholders), selectedPlates)

    # Commit changes and terminate the database connection
    conn.commit()
    conn.close()

    return "Record removed successfully", 200

@view.route('/detect', methods=['GET'])
def detect():
    return render_template("detect.html", user=current_user)

@view.route('/detect-result', methods=['GET', 'POST'])
def detectResult():
    # Establish database connection
    conn = sqlite3.connect('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/vehicleData.db')
    cursor = conn.cursor()

    # Fetch data from platesDetected table
    cursor.execute("SELECT * FROM platesDetected")
    data = cursor.fetchall()

    # Terminate connection
    conn.close()

    return render_template("detect-result.html", user=current_user, data=data)


@view.route('/upload', methods=['GET', 'POST'])
def uploadVideo():
    videoFile = request.files['videoFile']
    # Saving video to directory
    videoPath = '/Users/emanbegah/Desktop/' + videoFile.filename
    videoFile.save(videoPath)

    result = videoDetection(videoPath)

    # Establish database connection
    conn = sqlite3.connect('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/vehicleData.db')
    cursor = conn.cursor()

    # Fetch data from platesAuthorised table
    cursor.execute("SELECT * FROM platesDetected")
    data = cursor.fetchall()

    # Terminate connection
    conn.close()


    return render_template("detect-result.html", data=data, user=current_user)

@view.route('/report', methods=['GET', 'POST'])
def report():
    info = generateReport()

    return render_template("report.html", info=info, user=current_user)