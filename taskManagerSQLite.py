import re,sqlite3
from sqlite3 import Error
from os import system, name

sort_by = "name"
sort_order = "ASC"
'''
Uses system call to clear console, found online, not my own method
'''
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

'''
returns the max length of the name of a task, used to help keep the table "pretty"
'''
def getMaxTaskLength(conn):
    c = conn.cursor()
    c.execute('''SELECT name FROM todo_table''')
    x = 4
    for task in c.fetchall():
        if len(task[0]) > x:
            x = len(task[0])
    return x

'''
sorts task list by parameter, sorts by name,cost,priority, ease of use
'''
def sort(conn):
    global sort_by, sort_order
    c = conn.cursor()
    sort_input = input("Sort by name, cost, priority, or ease? ").lower()
    if len(sort_input) == 0:
        print("Empty sort type")
        return
    elif sort_input[0] == "n":
        sort_by = "name"
    elif sort_input[0] == "c":
        sort_by = "cost"
    elif sort_input[0] == "p":
        sort_by = "priority"
    elif sort_input[0] == "e":
        sort_by = "ease"
    else:
        print("Not valid sort type")
        return
    #asks user for order of sort too
    sort_input = input("Ascending or descending order? ").lower()
    if len(sort_input) == 0:
        print("Empty order type")
        return
    elif sort_input[0] == "a":
        sort_order = "ASC"
    elif sort_input[0] == "d":
        sort_order = "DESC"

'''
displays the list of tasks in a nice table format, which displays at the top of the screen
'''
def printTasks(conn):
    global sort_order, sort_by
    c = conn.cursor()
    c.execute('''SELECT * FROM todo_table ORDER BY ''' + sort_by +  " " + sort_order)
    index = 1
    maxString = getMaxTaskLength(conn)
    print('Task number'.ljust(14)+'|'+'Name'.center(maxString)+'|'+'Cost'.center(8)+'|'+'Priority'.center(8)+'|'+'Ease'.center(8)+'|')
    print('-'*(43+maxString))
    for row in c.fetchall():
        name,cost,priority,ease = row
        print(f'Task {index}:'.ljust(14) + f'|{name.center(maxString)}|{str(cost).center(8)}|{str(priority).center(8)}|{str(ease).center(8)}|')
        index+=1
    print('-'*(43+maxString))

'''
Prints list of commands
'''
def print_help():
    print("Enter:"+
        "\n1) '[add] task name and 3 numbers 0-10' for cost, priority, ease of project to add a task" +
        "\n2) '[sort]' for sorted list" +
        "\n3) '[remove] task name' to remove listed element" +
        "\n4) '[remove_number] n' to remove the nth task from the table" +
        "\n5) '[help]' to print command list" +
        "\n6) '[save]' to save current task list" +
        "\n7) '[quit]' to save and quit")

'''
removes task based on its name
'''
def remove(conn,mo):
    c =conn.cursor()
    if not mo:
        print("Not valid: use remove, name of task")
        return
    task = mo.group().strip()
    c.execute('''SELECT * FROM todo_table WHERE name=? ''',(task,))
    if(len(c.fetchall()) == 0):
        print("task not found")
    else:
        c.execute('''DELETE FROM todo_table WHERE name=?''',(task,))
        print("task \"" + task + "\" removed")

'''
removes task based on its number
'''
def remove_number(conn,mo,removeRegex):
    global sort_by, sort_order
    c = conn.cursor()
    if not mo:
        print("Not valid: use remove_number,followed by number to remove that task from the list")
        return
    taskNum = int(mo.group(1))
    c.execute('''SELECT * FROM todo_table ORDER BY ''' + sort_by +  " " + sort_order)
    task_list = c.fetchall()
    if(len(task_list) < taskNum or 0 >= taskNum):
        print("Task number does not exist")
    else:
        task_to_delete = task_list[taskNum - 1][0]
        remove(conn,removeRegex.search(" " + task_to_delete))#the space is needed to pass the regex

'''
This handles adding to the database
'''
def add(conn,mo):
    c = conn.cursor()
    if not mo:
        print("Not valid: use add, name of task, and 3 numbers 0-10 for cost,priority,ease of project")
        return
    taskName = mo.group(1).strip()
    task = [taskName,mo.group(2),mo.group(3),mo.group(4)]
    c.execute('''SELECT * FROM todo_table WHERE name=?''',(taskName,))
    if(len(c.fetchall()) != 0):
        print("task already in list...updating numerical values")
        c.execute('''UPDATE todo_table SET name=?,cost=?,priority=?,ease=?
        WHERE name=?''',task+[taskName])
    else:
        c.execute('''INSERT INTO todo_table(name,cost,priority,ease)
        VALUES(?,?,?,?) ''',task)
        print("Added \""+taskName+"\" to the list")

'''
initializes the tasks list by reading from the file and getting data to all the magic happen
'''
def init():
    try:
        conn = sqlite3.connect(r".\todolist.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS todo_table
        (name text NOT NULL UNIQUE,
        cost integer NOT NULL,
        priority integer NOT NULL,
        ease integer NOT NULL)''')
        return conn
    except Error as e:
        print(e)
        shutdown(conn)

'''
main body of code, a loop that handles IO/Regex, and basic functionality of the system
'''
def loop(conn):
    try:
        addRegex =  re.compile(r' +(.+) +(\d|10) +(\d|10) +(\d|10) *$')
        removeRegex = re.compile(r' +(.+) *$')
        numRegex = re.compile(r' +(\d+) *$')
        c = conn.cursor()
        print("Enter [help] for the list of commands")
        while True:
            printTasks(conn)
            new_input = input().strip()
            clear()
            if new_input.lower()[:4] == "quit":
                break
            elif new_input.lower()[:4] == "save":
                conn.commit()
            elif new_input.lower()[:4] == "sort":
                sort(conn)
            elif new_input.lower()[:13] =="remove_number":
                remove_number(conn,numRegex.search(new_input[13:]),removeRegex)#extra arg to call remove
            elif new_input.lower()[:6] == "remove":
                remove(conn,removeRegex.search(new_input[6:]))
            elif new_input.lower()[:3] == "add":
                add(conn,addRegex.search(new_input[3:]))
            elif new_input.lower()[:4] == "help":
                print_help()
            else:
                print("Enter a valid command")
    except KeyboardInterrupt or SystemExit:
        shutdown(conn)

'''
handles shutting code down by saving the current list of tasks into tasks.txt
'''
def shutdown(conn):
    conn.commit()
    conn.close()

'''
Main code, init the database, runs the loop, shuts down after the loop ends
'''
conn = init()
loop(conn)
shutdown(conn)
