import sqlite3
import pandas as pd
import datetime
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
				Date TEXT,
				Gm1 INTEGER,
				Gm2 INTEGER,
				Gm3 INTEGER,
				SS INTEGER,
				HCP INTEGER,
				HS INTEGER,
				Avg_Total INTEGER,
				Avg_Before INTEGER,
				Avg_Day INTEGER,
				Day_Avg_Delta INTEGER,
				Season_League TEXT,
				Bowler TEXT,
				MP_Gm1 INTEGER, 
				MP_Gm2 INTEGER, 
				MP_Gm3 INTEGER, 
				MP_Series INTEGER, 
				Match_Points INTEGER,
				Total_Avg_Delta INTEGER,
				Rank INTEGER,
				Team INTEGER,
				Position INTEGER,
				Pins INTEGER,
				Games INTEGER)''')
	
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
		
	
	def load_bowlingdata(self, bowling_df):

		# Get the column headers from the dataframe
		columns_headers = bowling_df.columns.values.tolist()
		
		# Iterates through the df loading each into the db
		for row in bowling_df.iterrows():
			row_values = row[1][columns_headers].tolist()
			self.UploadTableRow(table='bowling', columns_as_list=columns_headers, row_values_as_list=row_values)
			
	def clean_dfMatchPoints(self, df, datasetdate):
		
		# Correct date format from mm/dd/yyyy to yyyy-mm-dd
		# Convert the time column to datetime dtype
		df['Date_Formatted'] = pd.to_datetime(df['Date'], format="%m/%d/%Y")
		df['Date'] = df['Date_Formatted'].dt.strftime("%Y-%m-%d")
		
		# Slice df based upon datasetdate
		df = df[df['Date'] == datasetdate].copy()
		
		# Set the Bolwer column as the index
		df.set_index('Bowler', inplace=True)
		
		return df[['MP_Gm1', 'MP_Gm2', 'MP_Gm3', 'MP_Series', 'Match_Points']].copy()
	
	
	def DayDelta(self, row, startdate):
		
		timedelta = datetime.datetime.strptime(row['Date'], "%Y-%m-%d") - datetime.datetime.strptime(startdate, "%Y-%m-%d")
		return timedelta.days
		
		
	def UploadTableRow(self, table, columns_as_list, row_values_as_list):
		# Build query statement
		query_statement = "INSERT OR REPLACE INTO %s%s VALUES %s;" % (table, tuple(columns_as_list), tuple(row_values_as_list))
		
		# This corrects values that should be Null but in the string conversion are ''
		query_statement = query_statement.replace("''","NULL")
		query_statement = query_statement.replace('None',"NULL")
		
		# Uncomment to print the query, example query:
		# INSERT OR REPLACE INTO bowling('Bowler_Date', 'Days', 'Week', 'Date', 'Gm1', 'Gm2', 'Gm3', 'SS', 'HCP', 'Avg_Before', 'Avg_After', 
			# 'Avg_Today', 'Avg_Delta', 'Season_League', 'Bowler') VALUES ('ken-kite_2018-09-04', 0, 1, '2018-09-04', 134, 124, 142, 400, 93, 185, 133, 133, -52, '2018-19 Couples', 'ken-kite');
# 		print(query_statement)
		
		self.cur.execute(query_statement)
		
	def getuniquevalues(self, colummn, table):
		sql_statement = 'SELECT DISTINCT(%s) FROM %s;' % (colummn, table)
		return pd.read_sql_query(sql_statement, self.conn)
	
	def getUniqueBowlerValues_WhenSeasonLeague(self, seasonleague_lst):
		
		sl = "' OR Season_League = '".join(seasonleague_lst)
		sql_statement = "SELECT DISTINCT(Bowler) FROM Bowling wHERE Season_League = '{s}';".format(s=sl)
		
		return pd.read_sql_query(sql_statement, self.conn)
	
	def getUniqueTeams_WhenSeasonLeague(self, seasonleague_lst):
		
		sl = "' OR Season_League = '".join(seasonleague_lst)
		sql_statement = "SELECT DISTINCT(Team) FROM Bowling wHERE Season_League = '{s}';".format(s=sl)
		
		return pd.read_sql_query(sql_statement, self.conn)
	
	def getDaysSeries(self, df):
		# Calculate the number of days for each row relative to the 
		# first bowling date of that season league
		seasonleagues = df['Season_League'].unique().tolist()
		season_league_sliced_df = []
		
		for i, sl in enumerate(seasonleagues):
			season_league_sliced_df.append(df[df['Season_League'] == sl].copy()) # slice df for current season league
			sql_statement = """SELECT MIN(Date) From Bowling Where Season_League = '{s}';""".format(s=sl) # Get starting date for season league
			result = pd.read_sql_query(sql_statement, self.conn)
			startdate = result['MIN(Date)'].tolist()[0]
			
			season_league_sliced_df[i]['Days'] = season_league_sliced_df[i].apply(self.DayDelta, args=(startdate,), axis=1) # Apply number of days since season league start date
		
		df = pd.concat(season_league_sliced_df) # recombine sliced dataframes
		
		return df['Days']
	
	def getCumulativeMatchPointsSeries(self, df):
		# Add series with the cumulative summation of the match points 
		# Do this for each bowler & each season league.
		seasonleagues = df['Season_League'].unique().tolist()
		bowlers = df['Bowler'].unique().tolist()
		sliced_df = []
		df_index = 0
		
		# Slices dataframe by season league and by bowler
		# Then runs cumsum() on the match_points column
		# Finally each sliced DF is recombined
		# This ensures the cumsum() is calculated only on the data for a 
		# specified bowler and season league and does not inadvertantly combine
		# the summation across groups.
		for sl in seasonleagues:
			for b in bowlers:
				sliced_df.append(df[(df['Season_League'] == sl) & (df['Bowler'] == b)].copy())
				sliced_df[df_index]['Match_Points'] = sliced_df[df_index]['Match_Points'].replace('NULL', 0)
				sliced_df[df_index]['Cumulative_Match_Points'] = sliced_df[df_index]['Match_Points'].cumsum()
				df_index += 1
				
		result = pd.concat(sliced_df) # recombine sliced dataframes
		
		return result['Cumulative_Match_Points']
		
	
	def seriesScratch_query(self, columns, bowler, isIndividualBowlerSelection, seasonleagues):
		df = self.previewplot_query(columns, bowler, isIndividualBowlerSelection, seasonleagues)
		df['Avg_Total'] = df['Avg_Total']  * 3
		
		return df
	
	def previewplot_query(self, columns, bowler, isIndividualBowlerSelection, seasonleagues):
		
		# Comma seperates the selected columns
		# This will be instered into the query statement
		columns_comma_seperated = ', '.join(columns)
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		if isIndividualBowlerSelection:
			col = 'Bowler'
		else:
			col = 'Team'
			
		bowler_selection_spacer = "' OR {c} = '".format(c=col)
		bwl = bowler_selection_spacer.join(bowler)
		
		# Build Statement Query
		sql_statement = """
		SELECT 
			Date, 
			Season_league, 
			Team, 
			Bowler, 
			{c} 
		FROM Bowling 
		wHERE 
			({fc} = '{b}') AND 
			(Season_League = '{s}') AND 
			SS != 0 AND
			Position < 6
		ORDER BY 
			Season_League, 
			Bowler, 
			Date ASC;""".format(c=columns_comma_seperated, fc=col, b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days Columns
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def csvexport_query(self, columns, bowler, isIndividualBowlerSelection, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		columns_comma_seperated = ', '.join(columns)
		
		# If a team bowler selection is made
		# Query the db for a list of the 
		# bowlers that satisfy the user defined conditions
		if not isIndividualBowlerSelection:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT DISTINCT(Bowler) as Bowlers
			FROM Bowling
			WHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}');""".format(b=bwl, s=sl)
			bowler = pd.read_sql_query(sql_statement, self.conn)['Bowlers'].tolist()
		
		bwl = "' OR Bowler = '".join(bowler)
		
		## Build Statement Query
		sql_statement = """
		SELECT 
			Date, 
			Season_league, 
			Team, 
			Bowler, 
			{c} 
		FROM Bowling 
		wHERE 
			(Bowler = '{b}') AND 
			(Season_League = '{s}')
		ORDER BY 
			Season_League, 
			Bowler, 
			Date ASC;""".format(c=columns_comma_seperated, b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days & Cumulative_Match_Points Columns
		df['Days'] = self.getDaysSeries(df.copy())
		if 'Match_Points' in df.columns.values.tolist():
			df['Cumulative_Match_Points'] = self.getCumulativeMatchPointsSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def matchPointsCumSum_query(self, bowler, isIndividualBowlerSelection, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		if isIndividualBowlerSelection:
			col = 'Bowler'
		else:
			col = 'Team'
			
		bowler_selection_spacer = "' OR {c} = '".format(c=col)
		bwl = bowler_selection_spacer.join(bowler)
		
		## Build Statement Query
		sql_statement = """
		SELECT 
			Date, 
			Season_league, 
			Team, 
			Bowler, 
			Match_Points 
		FROM Bowling 
		wHERE 
			({c} = '{b}') AND 
			(Season_League = '{s}') AND
			SS != 0 AND
			Position < 6 AND
			TEAM IS NOT NULL AND
			TEAM != 0
		ORDER BY 
			Season_League, 
			Bowler, 
			Date ASC;""".format(c=col, b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days & Cumulative_Match_Points Columns
		df['Days'] = self.getDaysSeries(df.copy())
		df['Cumulative_Match_Points'] = self.getCumulativeMatchPointsSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def GameComparison_query(self, bowler, isIndividualBowlerSelection, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# If a team bowler selection is made
		# Query the db for a list of the 
		# bowlers that satisfy the user defined conditions
		if not isIndividualBowlerSelection:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT DISTINCT(Bowler) as Bowlers
			FROM Bowling
			WHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}');""".format(b=bwl, s=sl)
			bowler = pd.read_sql_query(sql_statement, self.conn)['Bowlers'].tolist()
		
		bwl = "' OR Bowler = '".join(bowler)
		
		# Build Statement Query
		bwl = "' OR Bowler = '".join(bowler)
		sql_statement = """
		SELECT 
			Date, 
			Season_league, 
			Team, 
			Bowler, 
			Gm1,
			Gm2,
			Gm3,
			Avg_Before
		FROM Bowling 
		wHERE 
			(Bowler = '{b}') AND 
			(Season_League = '{s}') AND
			SS != 0 AND
			Position < 6 AND
			TEAM IS NOT NULL AND
			TEAM != 0
		ORDER BY 
			Season_League, 
			Bowler, 
			Date ASC;""".format(b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days & Cumulative_Match_Points Columns
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		try:
			df = df[df['Gm1'] != 'NULL'].copy()
		except TypeError:
			pass
		
		return df
	
	def teamHandicap_query(self, bowler, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# There is a check to prevent an individual bowler selection,
		# Thus no bowler by team selections will pass the check
		bwl = "' OR Team = '".join(bowler)
		
		## Build Statement Query
		
		sql_statement = """
		SELECT 
			Season_League,
			Date,  
			Team, 
			SUM(
				CASE
					WHEN HS = 0
					THEN Gm1 + Gm2 + Gm3 + (HCP * 3)
					ELSE HS
				END) as Team_Handicap
		FROM Bowling 
		wHERE 
			(Team = '{b}') AND 
			(Season_League = '{s}')	AND 
			Position < 6
		GROUP BY
			Season_League, 
			Team, 
			Date 
		ORDER BY
			Season_League, 
			Team, 
			Date ASC;""".format(b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days Column
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def teamGameHCP_query(self, bowler, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# There is a check to prevent an individual bowler selection,
		# Thus no bowler by team selections will pass the check
		bwl = "' OR Team = '".join(bowler)
		
		## Build Statement Query
		
		sql_statement = """
		WITH InitialRowFilter_CalculateHCPBefore AS (
			SELECT
				Season_League,
				Date,  
				Team, 
				Gm1,
				Gm2,
				Gm3,
				CASE
					WHEN CAST((220 - Avg_Before) * 0.9 as INT) < 0 THEN 0
					ELSE CAST((220 - Avg_Before) * 0.9 as INT)
				END AS HCP_Before
			FROM Bowling 
			wHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}')	AND 
				Position < 6
		)
		SELECT 
			Season_League,
			Date,  
			Team, 
			Sum(Gm1 + HCP_Before) AS Gm1_Tm_HCP,
			Sum(Gm2 + HCP_Before) AS Gm2_Tm_HCP,
			Sum(Gm3 + HCP_Before) AS Gm3_Tm_HCP
		FROM InitialRowFilter_CalculateHCPBefore 
		GROUP BY
			Season_League, 
			Team, 
			Date 
		ORDER BY
			Season_League, 
			Team, 
			Date ASC;""".format(b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days Column
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def summaryTable_query(self, bowler, isIndividualBowlerSelection, seasonleagues):
		
		# Build WHERE conditions that will be inserted into the final query statement
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# If a team bowler selection is made
		# Query the db for a list of the 
		# bowlers that satisfy the user defined conditions
		if not isIndividualBowlerSelection:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT DISTINCT(Bowler) as Bowlers
			FROM Bowling
			WHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}');""".format(b=bwl, s=sl)
			bowler = pd.read_sql_query(sql_statement, self.conn)['Bowlers'].tolist()
		
		bwl = "' OR Bowler = '".join(bowler)
		
		
		## Build Statement Query
		sql_statement = """
		WITH InitialRowFilter AS (
			SELECT 
				Date,
				Team,
				(Season_league || '_' || Bowler) AS id,
				Season_league, 
				Bowler,
				Gm1,
				Gm2,
				Gm3,
				Avg_Total,
				Match_Points,
				SS,
				Rank
			FROM Bowling
			WHERE 
				(Bowler = '{b}') AND 
				(Season_League = '{s}') AND
				SS != 0 AND
				Position < 6 AND
				TEAM IS NOT NULL AND
				TEAM != 0
		),
			
		GameMaxMin_MatchPoints AS (
			SELECT
				id,
				Season_league, 
				Bowler,
				MIN(
					CASE
						WHEN Gm1 < Gm2 AND Gm1 < Gm3 THEN Gm1
						WHEN Gm2 < Gm1 AND Gm2 < Gm3 THEN Gm2
						Else Gm3
					End) As Min_Game,
				MAX(
					CASE
						WHEN Gm1 > Gm2 AND Gm1 > Gm3 THEN Gm1
						WHEN Gm2 > Gm1 AND Gm2 > Gm3 THEN Gm2
						Else Gm3
					End) As Max_Game,
				MIN(SS) as Low_Series,
				MAX(SS) as High_Series,
				SUM(Match_Points) As Total_Match_Points
			FROM InitialRowFilter 
			GROUP BY
				Season_League,
				Bowler
		),
		
		Starting_Total_Average AS (
			SELECT
				id,
				Date,
				Season_league, 
				Bowler,
				MIN(Date) AS Start_Date,
				Avg_Total AS Start_Avg
			FROM InitialRowFilter
			Group BY
				Season_League,
				Bowler
			HAVING
				MIN(Date) = Date
		),
		
		Current_Total_Average AS (
			SELECT
				id,
				Date,
				Season_league, 
				Bowler,
				MAX(Date) AS Current_Date,
				Avg_Total AS Current_Avg,
				Rank
			FROM InitialRowFilter
			Group BY
				Season_League,
				Bowler
			HAVING
				MAX(Date) = Date
		)
					
		SELECT
			GameMaxMin_MatchPoints.Season_League,
			GameMaxMin_MatchPoints.Bowler,
			CASE 
				WHEN GameMaxMin_MatchPoints.Min_Game IS NULL THEN 0
				WHEN GameMaxMin_MatchPoints.Min_Game = 'NULL' THEN 0
				ELSE GameMaxMin_MatchPoints.Min_Game
			END AS Low_Game,
			CASE
				WHEN GameMaxMin_MatchPoints.Max_Game IS NULL THEN 0
				WHEN GameMaxMin_MatchPoints.Max_Game = 'NULL' THEN 0
				ELSE GameMaxMin_MatchPoints.Max_Game
			END AS High_Game,
			CASE
				WHEN GameMaxMin_MatchPoints.Low_Series IS NULL THEN 0
				WHEN GameMaxMin_MatchPoints.Low_Series = 'NULL' THEN 0
				ELSE GameMaxMin_MatchPoints.Low_Series
			END AS Low_series,
			CASE
				WHEN GameMaxMin_MatchPoints.High_Series IS NULL THEN 0
				WHEN GameMaxMin_MatchPoints.High_Series = 'NULL' THEN 0
				ELSE GameMaxMin_MatchPoints.High_Series
			END AS High_series,
			CASE
				WHEN GameMaxMin_MatchPoints.Total_Match_Points = '' THEN 0
				WHEN GameMaxMin_MatchPoints.Total_Match_Points IS NULL THEN 0
				ELSE GameMaxMin_MatchPoints.Total_Match_Points
			END AS Match_Pts,
			Starting_Total_Average.Start_Avg,
			Starting_Total_Average.Start_Date,
			Current_Total_Average.Current_Avg,
			Current_Total_Average.Current_Date,
			Current_Total_Average.Rank
			
		FROM GameMaxMin_MatchPoints
		INNER JOIN Starting_Total_Average ON Starting_Total_Average.id = GameMaxMin_MatchPoints.id
		INNER JOIN Current_Total_Average ON Current_Total_Average.id = GameMaxMin_MatchPoints.id
		ORDER BY GameMaxMin_MatchPoints.id ASC;
		""".format(b=bwl, s=sl)
			
		df = pd.read_sql_query(sql_statement, self.conn)
		
		df.fillna(0, inplace=True)
		
		return df
	
	def NormalizeDatabase(self):
		self.removeNullRows()
		self.correctNullValuesInTemporaryBowlers()
		self.correctInvalidTotal_Avg_Delta_Rows()
		
	def removeNullRows(self):
		# Null rows are the result of temp bowlers not bowling a particular night.  Or they 
		# arise from team  bowlers having entries before they joined the team.
		# They contain no useful data and muddy the waters with other queries.  
		# Note, many of the results will be "NULL" and Team = 0.
		
		
		# Removes temp bowlers in the league db not bowling a particular night
		query_statement = "DELETE FROM Bowling WHERE Gm1 = 'NULL';" 
		self.cur.execute(query_statement)
		
		# Removes bowlers on a team with a NULL row
		# Bowler has an entry with a date prior to them joining the team
		# example Tyler Dye missing the 1st night, he's in the league db, and part of an existing team
		query_statement = "DELETE FROM Bowling WHERE Team = 'NULL' and SS = 0;" 
		self.cur.execute(query_statement)
	
	def correctNullValuesInTemporaryBowlers(self):
		
		self.setTeamValueForTempBowlers() # Sets the team name for temp bowlers = 'temp'
		
		# Sets the position value for temp bowlers = 0 because it is not known, 
		# but it must be less than 6 to be allowed to pass through must analytically useful queries downstream
		self.setPositionValueForTempBowlers() 

		df = self.getTempBowlerRows()
		
		df['HCP'] = df.apply(self.calculate_HCP, axis=1)
		df['Games'] = df.apply(self.game_count, axis=1)
		df['Avg_Total'] = df.apply(self.calculate_Avg_Total, axis=1)
		df['Rank'] = df.apply(self.rankbowlers, axis=1)
		
		
		self.load_bowlingdata(df)
		self.CommitDB()
		
		df = self.getTempBowlerRows()
		df['Total_Avg_Delta'] = df.apply(self.calculate_Total_Avg_Delta, axis=1)
		
		
		self.load_bowlingdata(df)
		self.CommitDB()
		
	def correctInvalidTotal_Avg_Delta_Rows(self):
		df = self.getInvalidTotal_Avg_Delta_Rows()
		
		# If False then there are no Invalid Total_Avg_Delta Rows to correct
		if df.shape[0] != 0:
			df['Total_Avg_Delta'] = df.apply(self.calculate_Total_Avg_Delta, axis=1)
			
			self.load_bowlingdata(df)
			self.CommitDB()
		
	def setTeamValueForTempBowlers(self):
		# When temps bowl they are  placed on Team = "Null"
		# This will be replaced with Team = "Temp"
		
		query_statement = "UPDATE Bowling Set Team = 'Temp' WHERE Team = 'NULL';"
		self.cur.execute(query_statement)
	
	def setPositionValueForTempBowlers(self):
		
		query_statement = "UPDATE Bowling Set Position = 0 WHERE Team = 'Temp';"
		self.cur.execute(query_statement)
	
	
	def getInvalidTotal_Avg_Delta_Rows(self):
		query_statement = "SELECT * FROM Bowling WHERE Total_Avg_Delta = '-9999';"
		return pd.read_sql_query(query_statement, self.conn)
	
	def getTempBowlerRows(self):
		
		query_statement = "SELECT * FROM Bowling WHERE Team = 'Temp';"
		return pd.read_sql_query(query_statement, self.conn)	
	
	def calculate_Avg_Total(self, row):
		query_statement = """SELECT SUM(Gm1 + Gm2 + Gm3) AS Total_Pins
							 FROM Bowling 
 							 WHERE 
 								Season_League = '{s}' AND
 								Bowler = '{b}' AND
 								Date <= '{d}' AND
 								SS != 0;""".format(s=row['Season_League'], b=row['Bowler'], d=row['Date'])
		df = pd.read_sql_query(query_statement, self.conn)
		Total_Pins = df['Total_Pins'].tolist()[0]
		return int(Total_Pins / row['Games'])
	
	def game_count(self, row):
		# returns the number of games played up to that rows date 
		query_statement = """SELECT COUNT(Date) FROM Bowling 
 							WHERE 
 								Season_League = '{s}' AND
 								Bowler = '{b}' AND
 								Date <= '{d}' AND
 								SS != 0;""".format(s=row['Season_League'], b=row['Bowler'], d=row['Date'])
		df = pd.read_sql_query(query_statement, self.conn)
		bowling_outings_count = df['COUNT(Date)'].tolist()[0]
		return bowling_outings_count * 3
	
	def calculate_HCP(self, row):
		
		return int((row['HS'] - row['SS']) / 3)
	
	def calculate_Total_Avg_Delta(self, row):
		

		query_statement = """SELECT MIN(Date) FROM Bowling 
 							WHERE 
 								Season_League = '{s}' AND
 								Bowler = '{b}' AND
 								SS != 0;""".format(s=row['Season_League'], b=row['Bowler'])
		df = pd.read_sql_query(query_statement, self.conn)
		starting_date = df['MIN(Date)'].tolist()[0]
		
		query_statement = """SELECT Avg_Total FROM Bowling 
 							WHERE 
 								Season_League = '{s}' AND
 								Bowler = '{b}' AND
 								Date = '{d}' AND
 								SS != 0;""".format(s=row['Season_League'], b=row['Bowler'], d=starting_date)

		df = pd.read_sql_query(query_statement, self.conn)
		starting_average = df['Avg_Total'].tolist()[0]
								
		return row['Avg_Total'] - starting_average
		
	
	def rankbowlers(self, row):
		# Bowler must bowl in >= 40% of max games bowled to be ranked
		
		query_statement = """SELECT * FROM Bowling 
 							WHERE 
 								Season_League = '{s}' AND
 								Date = '{d}';""".format(s=row['Season_League'], d=row['Date'])
		df = pd.read_sql_query(query_statement, self.conn)
		
		min_games_required = df['Games'].max() * 0.4
		
		if row['Games'] >= min_games_required:
			return len(df[(df['Avg_Total'] > row['Avg_Total']) & (df['Games'] >= min_games_required)]) + 1
		else:
			return 0