import os
import sys
import logging.handlers
import logging

# For more options see: 
# https://www.geeksforgeeks.org/logging-in-python/ 
# https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler


#-- General setup --#
# Create `logs` folder path inside `backend` folder for file loggers
logs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
# Create `logs` folder if it doesn't exist
os.makedirs(logs_dir, exist_ok=True)


#-- Loggers --#

# Console logger
consoleLogger = logging.getLogger('consoleLogger')
consoleLogger.setLevel(logging.DEBUG)

# Timed Rotating File logger
timeFileLogger = logging.getLogger('timeFileLogger')
timeFileLogger.setLevel(logging.DEBUG)


#-- Handlers --#

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Timed Rotating File handler
time_file_handler = logging.handlers.TimedRotatingFileHandler(f"{logs_dir}/timed_rotating.log", when='midnight', interval=1, backupCount=10)


#-- Formatters --#

# Console formatter
consoleFormatter = logging.Formatter('\n\n %(name)s \n\n %(levelname)s: \n\n %(asctime)s \n\n %(message)s \n\n')

# Timed Rotating File formatter
timeFileFormatter = logging.Formatter('\n %(name)s \n\n %(levelname)s: \n %(asctime)s \n %(message)s \n\n-----')



#-- Set a formatter on a handler --#
console_handler.setFormatter(consoleFormatter)
time_file_handler.setFormatter(timeFileFormatter)

#-- Add a handler to a logger --#
consoleLogger.addHandler(console_handler)
timeFileLogger.addHandler(time_file_handler)
