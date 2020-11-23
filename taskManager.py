import re
from os import system, name

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
def getMaxTaskLength(tasks):
    x = 4
    for task in tasks:
        if len(task[0]) > x:
            x = len(task[0])
    return x

'''
displays the list of tasks in a nice table format, which displays at the top of the screen
'''
def printTasks(tasks):
    maxString = getMaxTaskLength(tasks)
    print('Task number'.ljust(14)+'|'+'Name'.center(maxString)+'|'+'Cost'.center(8)+'|'+'Priority'.center(8)+'|'+'Ease'.center(8)+'|')
    print('-'*(43+maxString))
    for index,task in enumerate(tasks):
        print(f'Task {index + 1}:'.ljust(14) + f'|{task[0].center(maxString)}|{task[1].center(8)}|{task[2].center(8)}|{task[3].center(8)}|')

'''
initializes the tasks list by reading from the file and getting data to all the magic happen
'''
def init(tasks):
    regex =  re.compile(r'(.+) +(\d|10) +(\d|10) +(\d|10)')
    f = open("tasks.txt",'r+')
    f_lines = f.readlines()
    for x in f_lines:
        mo=regex.search(x)
        tasks.append(list(mo.groups()))
        #tasks.append(x.strip("\n"));
    f.close()

'''
handles shutting code down by saving the current list of tasks into tasks.txt
'''
def shutdown(tasks):
    f = open("tasks.txt",'r+')
    f.seek(0)
    f.truncate(0)
    for task in tasks:
        f.write(f'{task[0]} {task[1]} {task[2]} {task[3]}\n');
    f.close()

'''
sorts task list by parameter, sorts by name,cost,priority, ease of use
'''
def sort(tasks,sorttype):
    if len(sorttype) == 0:
        print("Empty sort type")
        return
    if sorttype[0] == "n":
        tasks.sort(key=lambda l:l[0].lower())
    elif sorttype[0] == "c":
        tasks.sort(key=lambda l:l[1])
    elif sorttype[0] == "p":
        tasks.sort(key=lambda l:l[2])
    elif sorttype[0] == "e":
        tasks.sort(key=lambda l:l[3])
    else:
        print("Not valid sort type")

'''
main body of code, a loop that handles IO/Regex, and basic functionality of the system
'''
def loop(tasks):
    try:
        addRegex =  re.compile(r' +(.+) +(\d|10) +(\d|10) +(\d|10) *$')
        removeRegex = re.compile(r' +(.+) *$')
        numRegex = re.compile(r' +(\d+) *$')
        while True:
            printTasks(tasks)
            print("Enter:"+
            "\n1) '[add] task name and 3 numbers 0-10' for cost, priority, ease of project to add a task" +
            "\n2) '[sort]' for sorted list" +
            "\n3) '[remove] task name' to remove listed element" +
            "\n4) '[remove_number] n' to remove the nth task from the table"+
            "\n5) '[save]' to save current task list"
            "\n6) '[quit]' to save and quit")
            x = input().strip()
            clear()
            if x[:4] == "quit":
                break
            elif x[:4] == "save":
                shutdown(tasks)
            elif x[:4] == "sort":
                sorttype= input("Sort by name, cost, priority, or ease? ")
                sort(tasks,sorttype.strip())
            elif x[:13] =="remove_number":
                mo = numRegex.search(x[13:])
                if not mo:
                    print("Not valid: use remove_number,followed by number to remove that task from the list")
                    continue
                else:
                    taskNum = int(mo.group(1))
                    if len(tasks) < taskNum or 0 >= taskNum:
                        print("Task number does not exist")
                    else:
                        del tasks[taskNum - 1]
            elif x[:6] == "remove":
                mo = removeRegex.search(x[6:])
                if not mo:
                    print("Not valid: use remove, name of task")
                    continue
                task = mo.group().strip()
                found = False
                for taskList in tasks:
                    if task == taskList[0]:
                        tasks.remove(taskList);
                        print("task \"" + task + "\" removed")
                        found = True
                        break
                if not found:
                    print("task not found")
            elif x[:3] == "add":
                mo = addRegex.search(x[3:])
                if not mo:
                    print("Not valid: use add, name of task, and 3 numbers 0-10 for cost,priority,ease of project")
                    continue
                taskName = mo.group(1).strip()
                task = [taskName,mo.group(2),mo.group(3),mo.group(4)]
                if task in tasks:
                    print("task already in list")
                    continue
                for otherTask in tasks:
                    if taskName == otherTask[0]:
                        tasks.remove(otherTask)
                        print("Updated priotities of task")
                        continue
                else:
                    tasks.append(task)
                    print("Added \""+taskName+"\" to the list")
            else:
                print("Enter a valid command")
    except KeyboardInterrupt or SystemExit:
        shutdown(tasks)

#main code
tasks = []
init(tasks)
loop(tasks)
shutdown(tasks)
