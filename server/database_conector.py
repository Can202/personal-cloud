import sqlite3
import numpy as np

database = sqlite3.connect("Database.db")
database_queries = database.cursor()

	

def create_list_with_database(command):
	l = database_queries.execute(command).fetchall()
	return l
def create_array_with_database(command):
	array = np.array(database_queries.execute(command).fetchall())
	return array
def modify_database(command):
	database_queries.execute(command)
	database.commit()
