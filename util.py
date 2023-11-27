# ANPR Software for M.Sc. Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# Import Libraries
import easyocr
import pandas as pd

# EasyOCR Reader Initialization
reader = easyocr.Reader(['en'], gpu=False)


def extractVehicle(numberPlate, vehicleDetectionsInfo):
    x1, y1, x2, y2, confidence, classID = numberPlate

    vehicleFound = False

    for v in range(len(vehicleDetectionsInfo)):  # Iterating through each detection
        x1vehicle, y1vehicle, x2vehicle, y2vehicle, vehicleID = vehicleDetectionsInfo[v]

        # Check if number plate bounding box exists in region within a vehicle bounding box
        if x1 > x1vehicle and y1 > y1vehicle and x2 < x2vehicle and y2 < y2vehicle:
            vehicleIndex = v
            vehicleFound = True
            break

    # If TRUE, returns bounding box information and vehicleID of specific vehicle
    if vehicleFound:
        return vehicleDetectionsInfo[vehicleIndex]

    return -1, -1, -1, -1, -1


def extractNumberPlate(numPlateThreshold):
    extractions = reader.readtext(numPlateThreshold)
    for extraction in extractions:
        boundingBox, plate, confidence = extraction

        plate = plate.upper().replace(' ', '')

        plate = configurePlate(plate)

        return plate, confidence

    return None, None


# Map for Integer -> Character translation
int2charDict = {'0': 'O',
                '1': 'I',
                '2': 'Z',
                '4': 'A',
                '5': 'S',
                '6': 'G',
                '7': 'T'}

# Map for Character -> Integer translation
char2intDict = {'A': '4',
                'B': '8',
                'I': '1',
                'O': '0',
                'S': '5',
                'Z': '7'}


def configurePlate(plate):
    realPlate = ''  # Variable will store the formatted number plate
    # Conversion based on UK-Style Number Plate
    map = {0: int2charDict,
           1: int2charDict,
           2: char2intDict,
           3: char2intDict,
           4: int2charDict,
           5: int2charDict,
           6: int2charDict}

    indices = [0, 1, 2, 3, 4, 5, 6]  # Length of plate

    # Iteration through number plate to perform conversions if necesary
    for i in indices:
        if i < len(plate):
            if plate[i] in map[i].keys():
                realPlate += map[i][plate[i]]
            else:
                realPlate += plate[i]
        else:
            return False

    return realPlate


def writeResults(result, dest):  # Print results to CSV file used for database
    with open(dest, 'w') as file:  # Creating file and columns
        file.write('{},{},{},{},{},{},{}\n'.format('FrameID', 'VehicleID', 'VehicleBBox',
                                                   'NumPlateBBox', 'NumPlateBBoxConfidence', 'NumPlate',
                                                   'NumPlateConfidence'))

        for frameID in result.keys():
            for vehicleID in result[frameID].keys():
                print(result[frameID][vehicleID])
                if 'Vehicle' in result[frameID][vehicleID].keys() and \
                        'NumberPlate' in result[frameID][vehicleID].keys() and \
                        'plate' in result[frameID][vehicleID]['NumberPlate'].keys():
                    file.write('{},{},{},{},{},{},{}\n'.format(frameID,
                                                               vehicleID,
                                                               '[{} {} {} {}]'.format(
                                                                   result[frameID][vehicleID]['Vehicle'][
                                                                       'boundingBox'][0],
                                                                   result[frameID][vehicleID]['Vehicle'][
                                                                       'boundingBox'][1],
                                                                   result[frameID][vehicleID]['Vehicle'][
                                                                       'boundingBox'][2],
                                                                   result[frameID][vehicleID]['Vehicle'][
                                                                       'boundingBox'][3]),
                                                               '[{} {} {} {}]'.format(
                                                                   result[frameID][vehicleID]['NumberPlate'][
                                                                       'boundingBox'][0],
                                                                   result[frameID][vehicleID]['NumberPlate'][
                                                                       'boundingBox'][1],
                                                                   result[frameID][vehicleID]['NumberPlate'][
                                                                       'boundingBox'][2],
                                                                   result[frameID][vehicleID]['NumberPlate'][
                                                                       'boundingBox'][3]),
                                                               result[frameID][vehicleID]['NumberPlate'][
                                                                   'boundingBoxConfidence'],
                                                               result[frameID][vehicleID]['NumberPlate'][
                                                                   'plate'],
                                                               result[frameID][vehicleID]['NumberPlate'][
                                                                   'plateConfidence'])
                               )

        file.close()  # Close CSV file after appending


def writeAccurateResults(csvFile, destFile):
    df = pd.read_csv(csvFile)  # Read CSV file into DataFrame
    # Sort file by VehicleID and extract entries with highest plate confidence score
    highestScores = df.loc[df.groupby('VehicleID')['NumPlateConfidence'].idxmax()]
    # Ignore entries where NumPlate is False
    # df = df[df['NumPlate'] != False]
    highestScores = highestScores[highestScores['NumPlate'] != 'False']
    # Create new DataFrame with required information
    newDF = highestScores[['NumPlateConfidence', 'NumPlate']]
    newDF.to_csv(destFile, index=False)  # Write new DF in new CSV file
