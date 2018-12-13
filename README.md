# BowlingDataCenter

### Application Dependencies
1. Python 3.6.4
1. Windows10 64 bit
1. pandas==0.22.0
1. numpy==1.14.0
1. matplotlib==2.1.2
1. sqlite3
1. os
1. datetime
1. re
1. ntpath
1. json
1. fileinput
1. tkinter

### Application Description
ETL csv files downloaded from Bowling League website.  While the data is still in memory data is cleansed and linked so that primary and foreign keys can be generated prior to loading into a SQLite managed database.  A tkinter is used to create the GUI which allows the user to query the DB to generate customizable data visualizations.

### GUI & Application Example
![CLI](https://github.com/kitestring/BowlingDataCenter/blob/v1/Examples/Version1Demo_1.gif)