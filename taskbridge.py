from __future__ import print_function, unicode_literals
import json
import os
import re
import subprocess

import attr
import click
from tasklib import TaskWarrior


tw = TaskWarrior(data_location='~/.task', create=False)
TODO_TXT = os.path.expanduser('~/Dropbox/todo/todo.txt')
uid_re = re.compile('\[([0-9a-f]{8})\]')

@attr.s
class Todo:
    text = attr.ib()
    priority = attr.ib(default='A')
    done = attr.ib(default=False)
    tags = attr.ib(attr.Factory(list))
    contexts = attr.ib(attr.Factory(list))
    uuid = attr.ib(default=None)
    short_uuid = attr.ib(default=None)



_context_regex = re.compile(r'(?:^|\s+)(@\S+)')
_project_regex = re.compile(r'(?:^|\s+)(\+\S+)')
_creation_date_regex = re.compile(r'^'
                                  r'(?:x \d\d\d\d-\d\d-\d\d )?'
                                  r'(?:\(\w\) )?'
                                  r'(\d\d\d\d-\d\d-\d\d)\s*')
_due_date_regex = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
_priority_regex = re.compile(r'.{0,13}\(([A-Z])\) ')
_completed_regex = re.compile(r'^x (\d\d\d\d-\d\d-\d\d) ')


def load_todos():
    new = []
    deleted = []
    todos = []

    with open(TODO_TXT) as f:
        for line in f:
            priority, uid = None, None
            line = line.strip()

            done = line.startswith('x ')

            match = _priority_regex.match(line)
            if match:
                priority = match.group(1)

            match = uid_re.search(line)
            if match:
                uid = match.group(1)

            if uid or not done:
                todos.append(Todo(
                        text='blah',
                        priority=priority,
                        short_uuid=uid,
                        done=done))

            if uid_re.search(line):
                if line.startswith('x '):
                    deleted.append(line)
            else:
                if not line.startswith('x '):
                    new.append(line)
    #print(todos)

    return new, deleted


def short_id(uuid):
    return uuid[0:8]


def add_task(desc, priority=''):
    if priority:
        priority = 'pri:' + priority

    subprocess.check_output(['task', 'add', desc, priority])


def complete_task(short_id):
    for t in tw.tasks.pending():
        if t['uuid'].startswith(short_id):
            t.done()
            return True

    return False


def gen_todos():
    pending = sorted(tw.tasks.pending(), key=lambda x: x['urgency'], reverse=True)

    with open(TODO_TXT, 'w') as f:
        for p in pending:
            print('{} [{}]'.format(p['description'], short_id(p['uuid'])), file=f)


def update_tasks(new, deleted):
    for task in new:
        add_task(task)

    if len(new):
        print('Added {} new tasks'.format(len(new)))

    deleted_cnt = 0
    for task in deleted:
        m = uid_re.search(task)
        if complete_task(m.groups()[0]):
            deleted_cnt +=1

    if deleted_cnt:
        print('Completed {} tasks'.format(deleted_cnt))


@click.command()
def main():
    new, deleted = load_todos()
    update_tasks(new, deleted)
    gen_todos()


if __name__ == '__main__':
    main()
