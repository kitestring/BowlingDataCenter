import sqlite3
import pandas as pd
import time
from datetime import date
import os
import ntpath

class BowlingDB():
	def __init__(self, filepath):
		
		db_exists = self.validate_dbfilepath(filepath)
		self.conn = sqlite3.connect(filepath)
		self.cur = self.conn.cursor()
		if not db_exists: self.createtables()
		
# Need to fix this adding in the match points columns	
	def createtables(self):
		self.conn.execute('''
				CREATE TABLE bowling(
				Bowler_Date TEXT PRIMARY KEY,
				Days INTEGER,
				Week INTEGER,
				Date TEXT,
				Gm1 INTEGER,
				Gm2 INTEGER,
				Gm3 INTEGER,
				SS INTEGER,
				HCP INTEGER,
				HS INTEGER,
				Avg_Before INTEGER,
				Avg_After INTEGER,
				Avg_Today INTEGER,
				Avg_Delta INTEGER,
				Season_League TEXT,
				Bowler TEXT)''')
	
	def validate_dbfilepath(self, filepath):
		# checks if database exists
		if os.path.exists(filepath):
			return True
		else:
			return False
		
	def getTables(self):
		#returns a tuple list with all the table names from a given db connection
		self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		return self.cur.fetchall()
		
	def getColumns(self, table):
		#returns a list with all the column names from a given db connection
		column_query = self.conn.execute('SELECT * from %s' % table)
		x = [description[0] for description in column_query.description]
		return [description[0] for description in column_query.description]
		
	def closeDBConnection(self):
		self.conn.close()
		
	def CommitDB(self):
		self.conn.commit()
		
	def load_DataFrame(self, df, table_name):
		df.to_sql(table_name, self.conn, if_exists="append")
		
	def load_Data(self, df, table_name):
		#executemany - I couldn't for the life of me get executemany to work...?
		# http://jpython.blogspot.com/2013/11/python-sqlite-example-executemany.html
		data, columns = self.createListOfTuples(df, table_name)
		
		for row in data:
			try:
				self.conn.execute("INSERT INTO %s %s VALUES %s" % (table_name, columns, row))
			except sqlite3.IntegrityError:
				print("Record Overwritten\n\tTable: %s\n\tID: %s\n" % (table_name, row[0]))
				self.conn.execute("DELETE FROM %s WHERE id = '%s'" % (table_name, row[0]))
				self.conn.execute("INSERT INTO %s %s VALUES %s" % (table_name, columns, row))
		
	def clearDB(self):
		
		for key_table, value in self.schema.items():
			self.conn.execute("DELETE FROM %s" % key_table)	
	
	def loadcsvfile(self, csvfilepath, Season_League):

		df = pd.read_csv(csvfilepath)
		df = self.clean_df(df, csvfilepath, Season_League)
		
		# Get the table column headers
		columns_headers = self.getColumns('bowling')
		
		# Remove match point columns
		for i in ['MP_Gm1', 'MP_Gm2', 'MP_Gm3', 'MP_Series', 'Match_Points']:
			while i in columns_headers:
				columns_headers.remove(i)
		
		# Iterates through the df loading each into the db
		for row in df.iterrows():
			row_values = row[1][columns_headers].tolist()
			self.UploadTableRow(table='bowling', columns_as_list=columns_headers, row_values_as_list=row_values)
			
	def loadexcelfile(self, excelfilepath):
		
		df = pd.read_excel(excelfilepath)
		dfMatchPoints = self.clean_dfMatchPoints(df)
		
		# Iterates through the df loading each into the db
		for row in dfMatchPoints.iterrows():
			row_values = row[1][['Bowler_Date', 'MP_Gm1', 'MP_Gm2', 'MP_Gm3', 'MP_Series', 'Match_Points']].tolist()
			self.UpdateRow_MatchPoint(row_values)
		
		
	def clean_dfMatchPoints(self, df):
		
		# Correct date format from mm/dd/yyyy to yyyy-mm-dd
		# Convert the time column to datetime dtype
		df['Date_Formatted'] = pd.to_datetime(df['Date'], format="%m/%d/%Y")
		df['Date'] = df['Date_Formatted'].dt.strftime("%Y-%m-%d")
		
		# Create the primary key which is Bowler_Date
		df['Bowler_Date'] = df['Bowler'] + '_' + df['Date']
		
		return df[['Bowler_Date', 'MP_Gm1', 'MP_Gm2', 'MP_Gm3', 'MP_Series', 'Match_Points']].copy()
	
	def clean_df(self, df, csvfilepath, Season_League):
		
		df.rename(index=str, columns={"Avg<br />Before": "Avg_Before", "Avg<br />After": "Avg_After", "Date": "Date_Formatted",
									"Todays<br />Avg": "Avg_Today", "+/-<br />Avg": "Avg_Delta"}, inplace=True)
		# extracts bowler name from file name, example file name: ken-kite-history.csv
		df['Bowler'] = ntpath.basename(csvfilepath).replace('-history','').replace('.csv','')
		
		# Correct date format from mm/dd/yyyy to yyyy-mm-dd
		# Convert the time column to datetime dtype
		df['Date_Formatted'] = pd.to_datetime(df['Date_Formatted'], format="%m/%d/%Y")
		df['Date'] = df['Date_Formatted'].dt.strftime("%Y-%m-%d")
		
		# Create the primary key which is Bowler_Date
		df['Bowler_Date'] = df['Bowler'] + '_' + df['Date']
		
		# Create a Days column which counts the number of days from the first date of that season_league
		df['Days'] = df.apply(self.DayDelta, args=(df['Date_Formatted'].min(),), axis=1)
		df.drop(['Date_Formatted'], axis=1, inplace=True)
		
		df['Season_League'] = Season_League
		
		return df
	
	def DayDelta(self, row, startdate):
		timedelta = row['Date_Formatted'] - startdate
		return timedelta.days
		
	
	def UpdateRow_MatchPoint(self, row_values_as_list):
		Bowler_Date = row_values_as_list[0]
		MP_Gm1 = row_values_as_list[1]
		MP_Gm2 = row_values_as_list[2]
		MP_Gm3 = row_values_as_list[3]
		MP_Series = row_values_as_list[4]
		Match_Points = row_values_as_list[5]
		
		
		query_statement = """Update bowling 
							SET MP_Gm1 = '{G1}', 
								MP_Gm2 = '{G2}', 
								MP_Gm3 = '{G3}', 
								MP_Series = '{MPS}', 
								Match_Points = '{MPT}'
							WHERE Bowler_Date = '{BD}';""".format(G1=MP_Gm1, G2=MP_Gm2, G3=MP_Gm3, MPS=MP_Series, MPT=Match_Points, BD=Bowler_Date)
							
		query_statement = query_statement.replace("nan","NULL")
		
		self.cur.execute(query_statement)
		
	def UploadTableRow(self, table, columns_as_list, row_values_as_list):
		# This corrects values that should be Null but in the string conversion are ''
		query_statement = "INSERT OR REPLACE INTO %s%s VALUES %s;" % (table, tuple(columns_as_list), tuple(row_values_as_list))
# 		query_statement = query_statement.replace("''","NULL")
		
		# Uncomment to print the query, example query:
		# INSERT OR REPLACE INTO bowling('Bowler_Date', 'Days', 'Week', 'Date', 'Gm1', 'Gm2', 'Gm3', 'SS', 'HCP', 'Avg_Before', 'Avg_After', 
			# 'Avg_Today', 'Avg_Delta', 'Season_League', 'Bowler') VALUES ('ken-kite_2018-09-04', 0, 1, '2018-09-04', 134, 124, 142, 400, 93, 185, 133, 133, -52, '2018-19 Couples', 'ken-kite');
		# print(query_statement)
		
		self.cur.execute(query_statement)
		
	def getuniquevalues(self, colummn, table):
		sql_statement = 'SELECT DISTINCT(%s) FROM %s;' % (colummn, table)
		return pd.read_sql_query(sql_statement, self.conn)
		
	def previewplotquery(self, columns, bowler, seasonleagues):
		
		# Build Query
		columns_comma_seperated = ', '.join(columns)
		sl = "' OR Season_League = '".join(seasonleagues)
		sql_statement = "SELECT {c} FROM Bowling wHERE Bowler = '{b}' AND (Season_League = '{s}') AND SS != '0' ORDER BY Season_League ASC;".format(c=columns_comma_seperated, b=bowler, s=sl)
		
		return pd.read_sql_query(sql_statement, self.conn)
	
	def plotreportquery(self, bowler, seasonleagues):
		
		# Build Query
		sl = "' OR Season_League = '".join(seasonleagues)
		sql_statement = "SELECT * FROM Bowling wHERE Bowler = '{b}' AND (Season_League = '{s}') AND SS != '0' ORDER BY Season_League ASC;".format(b=bowler, s=sl)
		
		return pd.read_sql_query(sql_statement, self.conn)