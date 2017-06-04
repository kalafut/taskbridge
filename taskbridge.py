from __future__ import print_function, unicode_literals
import json
import os
import re
import subprocess

import click

TODO_TXT = os.path.expanduser('~/Dropbox/todo/todo.txt')
uid_re = re.compile('\[([0-9a-f]{8})\]')

def load_todos():
    new = []
    deleted = []

    with open(TODO_TXT) as f:
        for line in f:
            line = line.strip()

            if uid_re.search(line):
                if line.startswith('x '):
                    deleted.append(line)
            else:
                if not line.startswith('x '):
                    new.append(line)

    return new, deleted


def short_id(task):
    return task['uuid'][0:8]


def add_task(desc, priority=''):
    if priority:
        priority = 'pri:' + priority

    subprocess.check_output(['task', 'add', desc, priority])


def complete_task(uuid):
    subprocess.check_output(['task', 'done', uuid])


def load_tasks():
    task_data = {
        'tasks': {},
        'pending': [],
        'deleted': [],
        'waiting': [],
        'completed': [],
        'recurring': []
        }

    for task in json.loads(subprocess.check_output(['task', 'export']).decode()):
        task_data['tasks'][short_id(task)] = task
        task_data[task['status']].append(task)

    return task_data


def gen_todos(task_data):
    pending = sorted(task_data['pending'], key=lambda x: x['urgency'], reverse=True)

    with open(TODO_TXT, 'w') as f:
        for p in pending:
            print('{} [{}]'.format(p['description'], short_id(p)), file=f)


def update_tasks(new, deleted):
    for task in new:
        add_task(task)

    if len(new):
        print('Added {} new tasks'.format(len(new)))

    for task in deleted:
        m = uid_re.search(task)
        complete_task(m.groups()[0])

    if len(deleted):
        print('Completed {} tasks'.format(len(deleted)))


def main():
    new, deleted = load_todos()
    update_tasks(new, deleted)
    task_data = load_tasks()
    gen_todos(task_data)


if __name__ == '__main__':
    main()
