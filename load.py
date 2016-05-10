import pymysql
import sys
import time
debug = True

#Drop the previous tables
#drop_existing_tables(cursor)
#Load in the new data

log = None

def write_log(statement):
	global log
	statement = str(statement)
	#print(statement)
	log.write(statement)
	log.write('\n')

def openDB():
	"Open a database connection and log file"
	global log
	# Open database connection
	db = pymysql.connect(host="100.15.105.119",user="adder",password="cmsc424",db="MondialDB")
	timestr = time.strftime("%Y%m%d-%H%M%S")
	log = open("loading_log"+timestr+".txt",'w')
	#cursor = db.cursor()
	return db

def close(db):
	"Close the database connection and the log file"
	#Disconnect from server
	db.close()
	log.close()

def safe_execute(db, sql):
	"Safely execute an SQL command"
	with db.cursor() as cursor:
		try:
			# Execute the SQL command													 
			cursor.execute(sql)
			# Commit changes in the database
			db.commit()
			return cursor.fetchall()
		except pymysql.DataError as e:
			write_log("Data Error " + str(e))
			db.rollback()
		except pymysql.ProgrammingError as e:
			write_log("Programming Error" + str(e))
			db.rollback()
		except pymysql.OperationalError as e:
			write_log("Operational Error" + str(e))
			db.rollback()
		except pymysql.IntegrityError as e:
			write_log("Integrity Error" + str(e))
			db.rollback()
		except pymysql.InternalError as e:
			write_log("Internal Error" + str(e))
			db.rollback()
		except pymysql.NotSupportedError as e:
			write_log("Not Supported Error" + str(e))
			db.rollback()
		except pymysql.InterfaceError as e:
			write_log("Interface Error" + str(e))
			db.rollback()
		except:
			# Rollback in case there is any error	
			write_log("A mysterious error occurred")
			db.rollback()

def insert_cup(db, name, year):	
	"Insert one world cup edition"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO Cup (CupYear,CupName) VALUES (" + year + ",'" + name + "');"
	write_log(sql)
	safe_execute(db, sql)
	
def retrieve_cups(db):
	"Get all the information from table Cup"
	sql = "SELECT * FROM Cup;"
	write_log(sql)
	results = safe_execute(db,sql)
	write_log(results)
	
def insert_match(db,match_id,cup_year,home_team,away_team,home_score,away_score,venue,stadium,month,day):
	"Insert one match"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `Game` (GameID, CupYear,TeamID1,TeamID2,Team1Score,Team2Score,Venue,Stadium,Month,Day) VALUES ("
	sql = sql + match_id + "," + cup_year + "," + home_team + "," + away_team + ","
	sql = sql + home_score + "," + away_score + "," + "'" + venue + "'" + "," + "'" + stadium + "'" + ","
	sql = sql + month + "," + day + ");"
	write_log(sql)
	results = safe_execute(db,sql)
	
def insert_team(db,team_id,name,flag):
	"Insert one team"
	#Use double quotes around country name because Côte d'Ivoire
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `Team` (TeamID, Name,Flag) VALUES ("
	sql = sql + team_id + ',"' + name + '","' + flag + '");'
	write_log(sql)
	results = safe_execute(db,sql)

def insert_team_cup_membership(db,team_id,cup_year,rank):
	"Insert one cup membership for the given team"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `CupMember` (TeamID, CupYear,Rank) VALUES ("
	sql = sql + team_id + ',' + cup_year + ',' + rank + ');'
	write_log(sql)
	results = safe_execute(db,sql)
	
def insert_goal(db,time,player_id,match_id,type,team_id):
	"Insert one goal for the given team and match and player"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `Goal` (Time, PlayerID,GameID,Type,TeamID) VALUES ("
	sql = sql + time + ',' + player_id + ',' + match_id + ",'" + type + "',"
	sql = sql + team_id + ');'
	write_log(sql)
	results = safe_execute(db,sql)

def insert_player(db,player_id,player_name,birthdate):
	"Insert player"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `Player` (PlayerID,Name,birthday) VALUES ("
	sql = sql + player_id + ",'" + player_name +"'," + birthdate + ');'
	write_log(sql)
	results = safe_execute(db,sql)
	
def insert_team_membership(db,cup_year,team_id,player_id):
	"Insert team membership"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO `TeamMember` (Year,TeamID,PlayerID) VALUES ("
	sql = sql + cup_year + "," + team_id +"," + player_id + ');'
	write_log(sql)
	results = safe_execute(db,sql)
	
def drop_existing_tables(db):
	"Drop certain tables if they already exist"
	safe_execute(db,"DROP TABLE IF EXISTS CUP")
	safe_execute(db,"DROP TABLE IF EXISTS CUP_MEMBER")
	safe_execute(db,"DROP TABLE IF EXISTS TEAM_MEMBER")
	safe_execute(db,"DROP TABLE IF EXISTS TEAM")
	safe_execute(db,"DROP TABLE IF EXISTS PLAYER")
	safe_execute(db,"DROP TABLE IF EXISTS PENALTY")
	safe_execute(db,"DROP TABLE IF EXISTS GOAL")
	safe_execute(db,"DROP TABLE IF EXISTS MATCH")

def create_player_table(db):
	sql = """CREATE TABLE PLAYER (
	FIRST_NAME  CHAR(20) NOT NULL,
	LAST_NAME  CHAR(20)),
	PID INTEGER,
	PRIMARY KEY (PID)
	"""
	safe_execute(db, sql)
	
def create_game_table(db):
	sql = """CREATE TABLE Game(
	MatchID int(11),
	CupYear YEAR(4),
	TeamID1 int(11),
	TeamID2 int(11),
	PRIMARY KEY (MatchID),
	CONSTRAINT fk_game_CupYear FOREIGN KEY (TeamID1) REFERENCES Team(TeamID),
	CONSTRAINT fk_game_TeamID1 FOREIGN KEY (TeamID2) REFERENCES Team(TeamID),
	CONSTRAINT fk_game_TeamID2 FOREIGN KEY (CupYear) REFERENCES Cup(CupYear)
	);"""
	safe_execute(sql)
