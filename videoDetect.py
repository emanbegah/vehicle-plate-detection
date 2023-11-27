# ANPR Software for MSc Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# Import Libraries and Dependencies
import cv2

from ultralytics import YOLO

from DatabaseModel.configDB import populateDetectedPlatesTable, clearCSVFile, generateReport
from sort.sort import *
from util import *


def videoDetection(videoPath):
    # Loading YOLOv8 Models
    cocoModel = YOLO('yolov8n.pt')  # For CAR detection
    numPlateModel = YOLO('Models/numberplates.pt')  # For NUMBER PLATE detection

    # Load Sample Video
    mov = cv2.VideoCapture(videoPath)

    # Array with Class ID of Vehicles within COCO Dataset
    vehicleList = [2, 3, 5, 7]  # CAR, MOTORBIKE, BUS, TRUCK

    # Creating a SORT instance for Multiple Object Tracking
    MotTracker = Sort()

    # # Dictionary for storing information of results extracted
    resultsDict = {}

    # Reading Video Frames
    frameID = -1
    status = True
    while status:
        frameID += 1  # frameID++ ???
        status, frame = mov.read()
        if status and 500 < frameID < 1000:  # Use this line for results produced in demo
        # if status and frameID < 20:
            # FrameID used as Key, for storing info for each frame
            resultsDict[frameID] = {}
            # Detection of Vehicle
            vehicleDetections = cocoModel(frame)[0]
            vehicleDetectionsInfo = []  # Array initialized to store bounding boxes of detected vehicles
            for detection in vehicleDetections.boxes.data.tolist():
                x1, y1, x2, y2, confidence, classID = detection
                if classID in vehicleList:
                    # IF valid vehicle detected then store bounding box details and confidence score
                    vehicleDetectionsInfo.append([x1, y1, x2, y2, confidence])

                # Tracking vehicle throughout video frames
                TrackingID = MotTracker.update(np.asarray(vehicleDetectionsInfo))

                # Number Plate Detections
                numPlateDetections = numPlateModel(frame)[0]
                for numberPlate in numPlateDetections.boxes.data.tolist():
                    # Store bounding box details and confidence score for detected number plate
                    x1, y1, x2, y2, confidence, classID = numberPlate

                # Assigning a Number Plate to a Vehicle
                x1vehicle, y1vehicle, x2vehicle, y2vehicle, vehicleID = extractVehicle(numberPlate, TrackingID)

                if vehicleID != -1:
                    # Image Preprocessing
                    numPlateCrop = frame[int(y1):int(y2), int(x1):int(x2), :]  # Crop detected number plate
                    numPlateGrayscale = cv2.cvtColor(numPlateCrop, cv2.COLOR_BGR2GRAY)  # Grayscale image
                    tFloat, numPlateThreshold = cv2.threshold(numPlateGrayscale, 64, 255,
                                                              cv2.THRESH_BINARY_INV)  # Threshold Image WATCH VIDEO

                    # Display Images
                    # cv2.imshow('Original', numPlateCrop)
                    # cv2.imshow('Threshold', numPlateThreshold)
                    # cv2.waitKey(0)

                    # Number Plate Extraction
                    numPlateResult, numPlateConfidence = extractNumberPlate(
                        numPlateThreshold)  # Returns result and confidence score

                    if numPlateResult is not None:
                        resultsDict[frameID][vehicleID] = {  # VehicleID used as Key 2 // Nested Dict Structure
                            'Vehicle': {'boundingBox': [x1vehicle, y1vehicle, x2vehicle, y2vehicle]},
                            'NumberPlate': {'boundingBox': [x1, y1, x2, y2],
                                            'plate': numPlateResult,
                                            'boundingBoxConfidence': confidence,
                                            'plateConfidence': numPlateConfidence}}

    # Clear CSV file (contains results from previous detection)
    clearCSVFile('/Users/emanbegah/Desktop/ANPR/Dev/realRecords.csv')
    print("Real Records Cleared")
    clearCSVFile('/Users/emanbegah/Desktop/ANPR/Dev/test2.csv')
    print("Test 2 Cleared")

    # Saving Results to file
    writeResults(resultsDict, 'test2.csv')
    print('Test 2 populated')
    writeAccurateResults('test2.csv', 'realRecords.csv')
    print('Real Records Populated')
    populateDetectedPlatesTable('/Users/emanbegah/Desktop/ANPR/Dev/realRecords.csv')
    print('DetectedPlates table populated.')

    generateReport()  # necessary?

    # MotTracker, resultsDict = resetData()

    print("Detection Complete + Report Generated.")


def resetData():
    MotTracker = Sort()  # Reinitialisation of the SORT tracker

    resultsDict = {}  # Clearing the results dictionary

    return MotTracker, resultsDict  # Return the reinitialised data structures
