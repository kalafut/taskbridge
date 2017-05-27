import json
import os
import re
import subprocess

TODO_TXT = os.path.expanduser('~/Dropbox/todo/todo.txt')

def load_todos():
    uid_re = re.compile('\[[0-9a-f]{8}\]')

    new = []
    deleted = []

    with open(TODO_TXT) as f:
        for line in f:
            line = line.strip()
            if line.startswith('x ') and uid_re.search(line):
                deleted.append(line)
            elif not uid_re.search(line):
                new.append(line)

    return new, deleted


def short_id(task):
    return task['uuid'][0:8]


def load_tasks():
    task_data = {
        'tasks': {},
        'pending': [],
        'deleted': [],
        'waiting': [],
        'completed': []
        }

    for task in json.loads(subprocess.check_output(['task', 'export'])):
        task_data['tasks'][short_id(task)] = task
        task_data[task['status']].append(task)

    return task_data

def gen_todos(task_data):
    pending = sorted(task_data['pending'], key=lambda x: x['urgency'], reverse=True)
    for p in pending:
        print('{} [{}]'.format(p['description'], short_id(p)))

task_data = load_tasks()
gen_todos(task_data)
print(load_todos())

#print(task_data)
