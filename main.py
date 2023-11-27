# ANPR Software for M.Sc. Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# Import Libraries
from DatabaseModel.configDB import setupDB, populateDetectedPlatesTable, populateAuthorisedPlatesTable
from webapp import createApplication

# Import Detection Logic

application = createApplication()
setupDB()
populateDetectedPlatesTable('/Users/emanbegah/Desktop/ANPR/Dev/realRecords.csv')
populateAuthorisedPlatesTable('/Users/emanbegah/Desktop/ANPR/Dev/DatabaseModel/platesAuthorised.csv')


if __name__ == '__main__':
    application.run(debug=True)  # Auto-reloads web server after changes
