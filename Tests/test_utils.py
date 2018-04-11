def open_json(file:str):
    with open(file, 'r') as myfile:
        data = myfile.read()
        return data

file = open_json('accepted_opp.json')
import json
data = json.loads(file)
from src.logic.Slack_Hub import hub
test = hub(data)