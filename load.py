import pymysql
import sys
import time
debug = True

#Drop the previous tables
#drop_existing_tables(cursor)
#Load in the new data

log = None

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
	global log
	#Disconnect from server
	db.close()
	log.close()

def safe_execute(db, sql):
	"Safely execute an SQL command"
	global log
	with db.cursor() as cursor:
		try:
			# Execute the SQL command													 
			cursor.execute(sql)
			# Commit changes in the database
			db.commit()
			return cursor.fetchall()
		except pymysql.DataError as e:
			log.write("Data Error " + str(e))
			db.rollback()
		except pymysql.ProgrammingError as e:
			log.write("Programming Error" + str(e))
			db.rollback()
		except pymysql.OperationalError as e:
			log.write("Operational Error" + str(e))
			db.rollback()
		except pymysql.IntegrityError as e:
			log.write("Integrity Error" + str(e))
			db.rollback()
		except pymysql.InternalError as e:
			log.write("Internal Error" + str(e))
			db.rollback()
		except pymysql.NotSupportedError as e:
			log.write("Not Supported Error" + str(e))
			db.rollback()
		except pymysql.InterfaceError as e:
			log.write("Interface Error" + str(e))
			db.rollback()
		except:
			# Rollback in case there is any error	
			log.write("A mysterious error occurred")
			db.rollback()

def insert_cup(db, name, year):	
	"Insert one world cup edition"
	global log
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	sql = "INSERT INTO Cup (CupYear,CupName) VALUES (" + year + ",'" + name + "');"
	log.write(sql)
	safe_execute(db, sql)
	
def retrieve_cups(db):
	"Get all the information from table Cup"
	sql = "SELECT * FROM Cup;"
	log.write(sql)
	results = safe_execute(db,sql)
	log.write(str(results))
	
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
