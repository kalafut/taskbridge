import json
import subprocess

task_data = json.loads(subprocess.check_output(['task', 'status:pending', 'export']))

for t in task_data:
    print(t['status'])


#print(task_data)
