import pymysql.cursors

debug = True

#Drop the previous tables
#drop_existing_tables(cursor)
#Load in the new data

def open():
	# Open database connection
	db = pymysql.connect(host="100.15.105.119",user="user",password="password",db="MondialDB",cursorclass=pymysql.cursors.DictCursor)
	#cursor = db.cursor()
	return db

def close(db):
	#Disconnect from server
	db.close()

def safe_execute(db, sql):
	cursor = db.cursor()
	try:
		# Execute the SQL command													 
		cursor.execute(sql)
		# Commit changes in the database
		db.commit()
	except:
		# Rollback in case there is any error											
		db.rollback()

def insert_cup(db, name,year):		
	"Insert one world cup edition"
	cursor = db.cursor()
	#INSERT INTO table_name (column1,column2,column3,...) VALUES (value1,value2,value3,...);
	#sql = "INSERT INTO CUP (CupYear,CupName) VALUES (" + year + "," + name + ");"
	print("TEST TEST TEST")
	#safe_execute(cursor, sql)
	
	
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
