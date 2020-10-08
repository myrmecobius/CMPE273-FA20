#%% Load packages
import sys
import schedule
import requests
import time
from datetime import datetime
import yaml

#%% Extract Data
if len(sys.argv) == 1:
    print("Error, no input to run")
    exit()

yaml_input = str(sys.argv[1])
with open(yaml_input) as file:
    input_list = yaml.load(file, Loader=yaml.FullLoader)

step_list = input_list["Steps"]
steps = dict()
if len(step_list) == 1:
    steps[1] = step_list[0]
else:
    for step in step_list:
        for k in step.keys():
            steps[k] = step[k]

when = input_list["Scheduler"]["when"]
step_ID = input_list["Scheduler"]["step_id_to_execute"][0]

http_dict = dict()
http_dict["http.response.code"] = 'response.status_code'
http_dict["http.response.headers.content-type"] = 'response.headers.get("content-type")'
http_dict["http.response.headers.X-Ratelimit-Limit"] = 'response.headers.get("X-Ratelimit-Limit")'

#%% Define functions
def getActionCmd( action, data ):
    if not action.startswith("::"):
        print("Invalid action")
        exit()
    if not data.startswith("response."):
        data = f"'{data}'"
    if action.startswith("::print"):
        return f"print({data})"
    elif action.startswith("::invoke"):
        new_step = action.split("::invoke:step:")
        step = int(new_step[1])
        return f"invoke({step}, {data})"

def invoke( sNum, data = '' ):
    if steps[sNum]["outbound_url"] == "::input:data":
        url = data
    else:
        url = steps[sNum]["outbound_url"]

    try:
        response = requests.get( url )
    except:
        print("Request Error: please check your wifi connection and url and try again")
        return

    equal_left = http_dict.get(steps[sNum]["condition"]["if"]["equal"]["left"], steps[sNum]["condition"]["if"]["equal"]["left"])
    equal_right = http_dict.get(steps[sNum]["condition"]["if"]["equal"]["right"], steps[sNum]["condition"]["if"]["equal"]["right"])
    if_cond = False
    if_cond_cmd = f"{equal_left} == {equal_right}"
    if_cond = eval(if_cond_cmd)

    if_action = steps[sNum]["condition"]["then"]["action"]
    if_data = http_dict.get(steps[sNum]["condition"]["then"]["data"], steps[sNum]["condition"]["then"]["data"])
    if_cmd = getActionCmd( if_action, if_data )

    else_action = steps[sNum]["condition"]["else"]["action"]
    else_data = http_dict.get(steps[sNum]["condition"]["else"]["data"], steps[sNum]["condition"]["else"]["data"])
    else_cmd = getActionCmd( else_action, else_data )

    if if_cond:
        exec(if_cmd)
    else:
        exec(else_cmd)

def printTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("timestamp", current_time)
    print()

#%% Define job to be scheduled
def job():
    invoke(step_ID)
    #printTime()

#%% Parse input and add to schedule
when = when.split(" ")
firstStar = (when[0] == '*')
secondStar = (when[1] == '*')
thirdStar = (when[2] == '*')

weekdays = {"0": "sunday", "1": "monday", "2": "tuesday", "3": "wednesday", "4": "thursday", "5": "friday", "6": "saturday", "7": "sunday", "*": "day"}

if secondStar and thirdStar and not firstStar:
    when0_good = ((when[0].isnumeric() and (0 <= int(when[0]))) and (int(when[0]) <= 59))
    if not when0_good:
        print(f'Minute does not support {when[0]}')
        exit()
    cmd = (f'schedule.every({when[0]}).minutes.do(job)')
    exec(cmd)
else:
    cmd = 'schedule.every()'
    when1_good = ((when[1].isnumeric() and (0 <= int(when[1]))) and (int(when[1]) <= 23)) or (when[1] == '*')
    when2_good = ((when[2].isnumeric() and (0 <= int(when[2]))) and (int(when[2]) <= 7)) or (when[2] == '*')
    if firstStar and secondStar and thirdStar:
        print("All * not supported")
        exit()    
    if not when1_good:
        print(f'Hour does not support {when[1]}')
        exit()
    if not when2_good:
        print(f"Day of week does not support {when[2]}")
        exit()
    h = ("0"*(2-len(when[1])) + when[1])*(when[1].isnumeric()) + "00"*(not when[1].isnumeric())
    m = ("0"*(2-len(when[0])) + when[0])*(when[0].isnumeric()) + "00"*(not when[0].isnumeric())
    cmd += "." + weekdays[(when[2])] + f".at({h}:{m}).do(job)"
    exec(cmd)

#%% Run on repeat
while True:
    schedule.run_pending()
    time.sleep(1)