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
    
#FAKE DATA IMPLEMENTATION
import threading
global i
i=-1
def change():
    global i
    threading.Timer(5.0,change).start()
    print(i)
    i = i+1
    if(i==10):
        i = 0

def fakeData(Dancer):
    global i
    threading.Timer(2.0, fakeData, args=[Dancer]).start()
    arr = ["shoutout","transition",
           "weightlift","transition",
           "muscle","transition",
           "shoutout","transition",
           "weightlift","transition"]
    if (arr[i] == "shoutout"):
        addValue(Dancer,"shoutout",1.0, 1.0, 1.0)
    elif (arr[i] == "weightlift"):
        addValue(Dancer, "weightlift",2.0, 3.0, 5.0)
    elif (arr[i] == "muscle"):
        addValue(Dancer,"muscle",3.0, 4.0, 4.0)
    elif (arr[i] == "transition"):
        addValue(Dancer, "transition", 0, 0, 0)
    #print(showTable("Dancer1"))
    

#testing
if __name__ == '__main__':
    #createTable("MLDancer1", "Dancer1")
    ##6 Beetles---------> Yaw,pitch,roll,X-Axis,Y-Axis,Z-Axis
    ##EMG ------------> mean amplitude(MeanAmp),root mean square amplitude(RMSAmp) mean frequency(MeanFreq)
##    createTable("Beetle3", "Yaw", "Pitch", "Row", "Xaxis", "Yaxis", "Zaxis")
    addValue("Beetle6", "-20.00", "-40.00", "-60.00", "-100.00", "-120.00", "-180.00")
##    for no in range(1,7):
##        showTable("Beetle" + str(no))
    
    #change()
    #fakeData("Dancer1")
    #fakeData("Dancer2")
    #fakeData("Dancer3")
    
    #createTable("Dancer3", "GroundTruth", "Yaw", "Pitch", "Roll")
    #showTable("Dancer3")
    #showTable("Dancer2")
    
    #clearTable("Dancer1")
    #addValue("test", "NEWNEWNNewValueHellos", "IdasdsssS", "32.0")
    #addValue("MLDancer1","dumbbell")
    #showTable("Hello")
    #getLastRow("testTable")
    #showTable("testTable")
    #print(getLastRow("testTable"))
    
