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
    query = "INSERT INTO " + tableName + " VALUES ("+ str(dataList).strip('[]') +")"#create query
    cursor.execute(query)
    connection.commit()
    count = cursor.rowcount
    print (count, "Value saved into " + tableName)
    
#Function to show all rows in Table
#Parameter: tableName - to specify the table name to be shown
def showTable(tableName):
    query = "SELECT * from " + tableName
    cursor.execute(query)
    print("Queried table from: " + tableName)
    table = cursor.fetchall()
    print(table)

#function to clear table 
def clearTable(tableName):
    query = "TRUNCATE " + tableName + "; DELETE FROM " + tableName +";"
    cursor.execute(query)
    connection.commit()


if __name__ == '__main__':
    #clearTable("testTable")
    addValue("testTable", "Hellos", "IS", "3.0")
    showTable("testTable")
