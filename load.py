import MySQLdb

debug = True


# Open database connection
db = MySQLdb.connect("localhost","user","password","MondialDB" )
cursor = db.cursor()

#Drop the previous tables
drop_existing_tables(cursor)
#Load in the new data

#Disconnect from server
db.close()

def safe_execute(cursor, sql):
    try:
        # Execute the SQL command                                                     
        cursor.execute(sql)
        # Commit changes in the database
        db.commit()
    except:
        # Rollback in case there is any error                                            
        db.rollback()

def drop_existing_tables(cursor):
    "Drop certain tables if they already exist"
    safe_execute(cursor,"DROP TABLE IF EXISTS CUP")
    safe_execute(cursor,"DROP TABLE IF EXISTS CUP_MEMBER")
    safe_execute(cursor,"DROP TABLE IF EXISTS TEAM_MEMBER")
    safe_execute(cursor,"DROP TABLE IF EXISTS TEAM")
    safe_execute(cursor,"DROP TABLE IF EXISTS PLAYER")
    safe_execute(cursor,"DROP TABLE IF EXISTS PENALTY")
    safe_execute(cursor,"DROP TABLE IF EXISTS GOAL")
    safe_execute(cursor,"DROP TABLE IF EXISTS MATCH")

def create_player_table(cursor):
    sql = 
    """CREATE TABLE PLAYER (
    FIRST_NAME  CHAR(20) NOT NULL,
    LAST_NAME  CHAR(20)),
    PID INTEGER,
    PRIMARY KEY (PID)
    """
    safe_execute(cursor, sql)
