import mysql.connector

host = input("Host: ")
user = input("User: ")
password = input("Password: ")
db = input("Database: ")

# host = "localhost"
# user = "root"
# password = "ayushaher"
# db = "avante"

mydb = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=db,
    auth_plugin='mysql_native_password',
)
mycursor = mydb.cursor(buffered=True)
path = input("Path of the file where you want to save: ")
actions = ["insert", "update", "delete"]


def init():
    mycursor.execute("SHOW tables")
    for x in mycursor.fetchall():
        if not str(x[0]).lower().startswith("vw_"):
            for table in x:
                for action in actions:
                    createTriggers(table, action, db)


def createTriggers(table, action, db):
    triggers = [
        f"\ncreate trigger {action}{table}trigger\n",
        f" after {action} on {db}.{table} \n",
        "FOR EACH ROW \n",
        "INSERT " + f"INTO {db}.audittrail\n",
        f' set action = "{action}",\n'
        'id = uuid(),\n',
        "createdon = sysdate(),\n",
        "updatedon = sysdate(),\n",
    ]

    mycursor.execute(f"show columns from {table}")
    lstColumns = mycursor.fetchall()
    nvalue = "nvalue=concat('{',"
    ovalue = "ovalue=concat('{',"
    for columns in lstColumns:
        columns = columns[0]
        nvalue += "'\"'" + f",'{columns}'," + "'\"'" + ",':'," + "'\"'" + f", new.{columns} ," + "'\",',"
        ovalue += "'\"'" + f",'{columns}'," + "'\"'" + ",':'," + "'\"'" + f", old.{columns} ," + "'\",',"
    nvalue = nvalue[:-1]
    nvalue += ",'}'),"
    ovalue = ovalue[:-1]
    ovalue += ",'}'),"

    if action == "insert":
        triggers.append(nvalue)
        triggers.append("\nuserid = NEW.createdby")
    elif action == "delete":
        triggers.append(ovalue)
        triggers.append("\nuserid = old.createdby")
    else:
        triggers.append(ovalue)
        triggers.append(nvalue)
        triggers.append("\nuserid = new.createdby")

    drop(table, action, db)
    triggers.append(";\n\n")
    # wFile = open(f"{path}\Triggers.sql", "w")
    file = open(f"{path}\Triggers.sql", "a")
    file.writelines(triggers)


def drop(table, action, db):
    dTriggers = f"drop trigger {db}.{action}{table}trigger;\n"
    file = open(f"{path}\Delete Triggers.sql", "a")
    file.writelines(dTriggers)


if __name__ == '__main__':
    try:
        init()
    except Exception as e:
        print(e)
