import pymysql
import sys

debug = True

#Drop the previous tables
#drop_existing_tables(cursor)
#Load in the new data

def open():
	# Open database connection
	db = pymysql.connect(host="100.15.105.119",user="adder",password="cmsc424",db="MondialDB")
	#cursor = db.cursor()
	return db

def close(db):
	#Disconnect from server
	db.close()

def safe_execute(db, sql):
	with db.cursor() as cursor:
		try:
			# Execute the SQL command													 
			cursor.execute(sql)
			# Commit changes in the database
			db.commit()
			return cursor.fetchall()
		except pymysql.DataError as e:
			print("Data Error " + str(e))
			db.rollback()
		except pymysql.ProgrammingError as e:
			print("Programming Error" + str(e))
			db.rollback()
		except:
			# Rollback in case there is any error	
			print("SOMETHING HAPPENED")
			db.rollback()

def insert_cup(db, name,year):		
	"Insert one world cup edition"
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO Cup (CupYear,CupName) VALUES (" + year + ",'" + name + "');"
	print(sql)
	safe_execute(db, sql)
	
def retrieve_cups(db):
	sql = "SELECT * FROM Cup;"
	print(sql)
	print("RESULTS---")
	results = safe_execute(db,sql)
	print(results)
	
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
