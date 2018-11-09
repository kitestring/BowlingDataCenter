from jsonAPI import JSON_Tools # @unresolvedimport
import os

# Initialize ProgramData directory & json file, if either doesn't exist then create the missing item
# Note, the JSON file contains db file path and all other instance data.  
# If JSON file not found then the default path will be used
utils_directory=os.path.join('C:\\', 'ProgramData', 'BowlingData')
jsonfilepath = os.path.join(utils_directory, 'bowlinginstancedata.txt')

db_filepath = os.path.join(utils_directory, 'bowling.db')
JSON_Tools().dump_Data_To_File(jsonfilepath, 
                               db_filepath = os.path.join(utils_directory, 'bowling.db'),
                               reports = {}, plots={})
