#%% Load packages
import sys
import schedule
import requests
import time
from datetime import datetime
import yaml

#%% Extract Data
yaml_input = str(sys.argv[1])
with open(yaml_input) as file:
    input_list = yaml.load(file, Loader=yaml.FullLoader)

sid = input_list["Step"]["id"]
stype = input_list["Step"]["type"]
method = input_list["Step"]["method"]
url = input_list["Step"]["outbound_url"]
condition = input_list["Step"]["condition"]

when = input_list["Scheduler"]["when"]
step_ID = input_list["Scheduler"]["step_id_to_execute"][0]

#%% Check for supported types
if step_ID != sid:
    print("Error: IDs do not match")
    exit()
elif method != "GET":
    print("Error: methods only supports GET")
    exit()

#%% Define job to be scheduled
def job():
    r = requests.get(url)
    if condition["if"]["equal"]["left"] == condition["if"]["equal"]["right"]: #PROBLEM
        data = condition["then"]["data"]
        cmd = condition["then"]["action"] + f"({data})"
        exec(cmd)
    else:
        data = condition["else"]["data"]
        cmd = condition["else"]["action"] + f"({data})"
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"timestamp", current_time)


#%% Parse input and add to schedule
when = when.split(" ")
cmds = [""] * 5

cmds[0] = (f'schedule.every({when[0]}).minutes.do(job)')*((when[0].isnumeric() and (0 <= int(when[0]))) and (int(when[0]) <= 59))
cmds[1] = (f'schedule.every({when[1]}).hours.do(job)')*((when[1].isnumeric() and (0 <= int(when[1]))) and (int(when[1]) <= 23))
cmds[2] = (f'schedule.every({when[2]}).minutes.do(job)')*((when[2].isnumeric() and (1 <= int(when[2]))) and (int(when[2]) <= 31))
cmds[3] = (f'schedule.every({when[3]}).minutes.do(job)')*((when[3].isnumeric() and (1 <= int(when[3]))) and (int(when[3]) <= 12))
cmds[4] = (f'schedule.every({when[4]}).minutes.do(job)')*((when[4].isnumeric() and (0 <= int(when[4]))) and (int(when[4]) <= 7))

for cmd in cmds:
    exec(cmd)

#%% Run on repeat
while True:
    schedule.run_pending()
    time.sleep(1)