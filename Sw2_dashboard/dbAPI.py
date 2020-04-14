#Developed by Gerald Chua Deng Xiang
import psycopg2 #import for DB

#Create the connection
connection = psycopg2.connect(user = "postgres",
                                  password = "Cg4002",
                                  host = "localhost",
                                  port = "5432",
                                  database = "postgres")
cursor = connection.cursor()

#Functions for CRUD

#Function to add a row
def addValue(tableName, *data):
    dataList = list(data) #convert multiple arguments into a list
    query = "INSERT INTO " + tableName + " VALUES ("+ str(dataList).strip('[]') +")" #inserts value into the table
    #query += "RETURNING " + str(dataList).strip('[]') #stores the last value that is being added
    cursor.execute(query)
    connection.commit()
    count = cursor.rowcount
    #lastRow = cursor.fetchone()#contains last row being stored
    print(count, "Value saved into " + tableName)
    print(query)
    #return lastRow

def addML(table, data):
    print(data)
    query = "INSERT INTO " + table + " VALUES ("+ data +")" #inserts value into the table
    #query += "RETURNING " + str(dataList).strip('[]') #stores the last value that is being added
    cursor.execute(query)
    connection.commit()
    count = cursor.rowcount
    #lastRow = cursor.fetchone()#contains last row being stored
    print(count, "Value saved into " + table)
    print(query)
    
    
#Function to show all rows in Table
#Parameter: tableName - to specify the table name to be shown
def showTable(tableName):
    query = "SELECT * from " + tableName 
    cursor.execute(query)
    print("Queried table from: " + tableName)
    table = cursor.fetchall()    
    print(table)

#Function to get last row in table
def getLastRow(tableName):
    query = "SELECT * from " + tableName 
    cursor.execute(query)
    #print("Queried table from: " + tableName)
    table = cursor.fetchall()
    return table[-1]


#function to clear table 
def clearTable(tableName):
    query = "TRUNCATE " + tableName + "; DELETE FROM " + tableName +";"
    cursor.execute(query)
    connection.commit()

#function to create a new table
def createTable(tableName, *columnNames):
    columns = list(columnNames)
    query = "CREATE TABLE " + tableName + " ("
    first = True
    for column in columns:
        if first:
            query += "\n" + column + " NUMERIC NOT NULL"
            first = False
        else:
            query += ", \n" + column + " NUMERIC NOT NULL"
    query += ");"
    cursor.execute(query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")
    

    
#testing
if __name__ == '__main__':
    x = 0#Do nothing

    
