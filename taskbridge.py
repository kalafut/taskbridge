from __future__ import print_function
import json
import os
import re
import subprocess

import click
from tasklib import TaskWarrior


tw = TaskWarrior(data_location='~/.task', create=False)
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


def short_id(uuid):
    return uuid[0:8]


def add_task(desc):
    priority_match = re.match(r'\(([A-C])\) +', desc)
    if priority_match:
        priority = 'pri:' + {'A': 'H', 'B': 'M', 'C': 'L'}[priority_match.group(1)]
        desc = desc[priority_match.span()[1]:]
    else:
        priority = ''

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
