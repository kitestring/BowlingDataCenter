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
		
		# Uncomment to print the query, example query:
		# INSERT OR REPLACE INTO bowling('Bowler_Date', 'Days', 'Week', 'Date', 'Gm1', 'Gm2', 'Gm3', 'SS', 'HCP', 'Avg_Before', 'Avg_After', 
			# 'Avg_Today', 'Avg_Delta', 'Season_League', 'Bowler') VALUES ('ken-kite_2018-09-04', 0, 1, '2018-09-04', 134, 124, 142, 400, 93, 185, 133, 133, -52, '2018-19 Couples', 'ken-kite');
# 		print(query_statement)
		
		self.cur.execute(query_statement)
		
	def getuniquevalues(self, colummn, table):
		sql_statement = 'SELECT DISTINCT(%s) FROM %s;' % (colummn, table)
		return pd.read_sql_query(sql_statement, self.conn)
	
	def getUniqueBowlerValuesWhenSeasonLeague(self, seasonleague_lst):
		
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
		
	def previewplot_query(self, columns, bowler, isIndividualBowlerSelection, seasonleagues):
		
		columns_comma_seperated = ', '.join(columns)
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# Build Statement Query
		if isIndividualBowlerSelection:
			bwl = "' OR Bowler = '".join(bowler)
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
				(Season_League = '{s}') AND 
				SS != 0 AND
				Position < 6
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(c=columns_comma_seperated, b=bwl, s=sl)
		else:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT 
				Date, 
				Season_league, 
				Team, 
				Bowler, 
				{c} 
			FROM Bowling 
			wHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}') AND 
				SS != 0 AND
				Position < 6 
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(c=columns_comma_seperated, b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days Columns
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def csvexport_query(self, columns, bowler, isIndividualBowlerSelection, seasonleagues):
		
		columns_comma_seperated = ', '.join(columns)
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# Build Statement Query
		if isIndividualBowlerSelection:
			bwl = "' OR Bowler = '".join(bowler)
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
		else:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT 
				Date, 
				Season_league, 
				Team, 
				Bowler, 
				{c} 
			FROM Bowling 
			wHERE 
				(Team = '{b}') AND 
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
		
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# Build Statement Query
		if isIndividualBowlerSelection:
			bwl = "' OR Bowler = '".join(bowler)
			sql_statement = """
			SELECT 
				Date, 
				Season_league, 
				Team, 
				Bowler, 
				Match_Points 
			FROM Bowling 
			wHERE 
				(Bowler = '{b}') AND 
				(Season_League = '{s}') AND
				Position < 6
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(b=bwl, s=sl)
		else:
			bwl = "' OR Team = '".join(bowler)
			sql_statement = """
			SELECT 
				Date, 
				Season_league, 
				Team, 
				Bowler, 
				Match_Points 
			FROM Bowling 
			wHERE 
				(Team = '{b}') AND 
				(Season_League = '{s}') AND
				Position < 6
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days & Cumulative_Match_Points Columns
		df['Days'] = self.getDaysSeries(df.copy())
		df['Cumulative_Match_Points'] = self.getCumulativeMatchPointsSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def GameComparison_query(self, bowler, isIndividualBowlerSelection, seasonleagues):
		
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# Build Statement Query
		if isIndividualBowlerSelection:
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
				Position < 6
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(b=bwl, s=sl)
		else:
			bwl = "' OR Team = '".join(bowler)
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
				(Team = '{b}') AND 
				(Season_League = '{s}') AND
				Position < 6
			ORDER BY 
				Season_League, 
				Bowler, 
				Date ASC;""".format(b=bwl, s=sl)
		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		# Create Days & Cumulative_Match_Points Columns
		df['Days'] = self.getDaysSeries(df.copy())
		
		# Change 'Date' column as dtype from an object (Text) to datetime 
		df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")	
		
		return df
	
	def teamHandicap_query(self, bowler, seasonleagues):
		
		sl = "' OR Season_League = '".join(seasonleagues)
		
		# Build Statement Query
		bwl = "' OR Team = '".join(bowler)
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
	
	def summaryTable_query(self, bowler, isIndividualBowlerSelection, seasonleagues):
		
		sl = "' OR Season_League = '".join(seasonleagues)
		
		
		## Build Statement Query
		
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
		
		sql_statement = """
		WITH InitialRowFilter AS (
			SELECT 
				Date,
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
				Position < 6
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
				MIN(Date),
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
			Current_Total_Average.Current_Avg,
			Current_Total_Average.Rank
		FROM GameMaxMin_MatchPoints
		INNER JOIN Starting_Total_Average ON Starting_Total_Average.id = GameMaxMin_MatchPoints.id
		INNER JOIN Current_Total_Average ON Current_Total_Average.id = GameMaxMin_MatchPoints.id
		ORDER BY GameMaxMin_MatchPoints.id ASC;
		""".format(b=bwl, s=sl)
			
		df = pd.read_sql_query(sql_statement, self.conn)
		
		df.fillna(0, inplace=True)
		
		return df
	
	
	
	def plotreportquery(self, bowler, seasonleagues):
		
		# Build Query
		sl = "' OR Season_League = '".join(seasonleagues)
		sql_statement = "SELECT * FROM Bowling wHERE Bowler = '{b}' AND (Season_League = '{s}') AND SS != '0' ORDER BY Season_League ASC;".format(b=bowler, s=sl)
		
		return pd.read_sql_query(sql_statement, self.conn)
	
	def manualDB_Corrections(self):
		query_statement = "UPDATE bowling SET Avg_Delta = 0 WHERE Bowler_Date = 'ken-kite_2018-09-04' or Bowler_Date = 'timothy-schramm_2018-09-11';"
		self.cur.execute(query_statement)
		