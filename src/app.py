from decouple import config
from flask import Flask, redirect, request, jsonify
import src.models.zoho_crm as Zoho
from urllib import parse
from src.logic.New_Opportunity import new_opportunity
from src.logic.Slack_Hub import hub
from src.logic.Assigned_Opportunity import assigned_opportunity

app = Flask(__name__)
logging = config('Logging', cast=bool)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Success'

@app.route('/auth', methods = ['GET'])
def auth():
    url = Zoho.Authorization.auth_url()
    return redirect(parse.quote(url))

@app.route('/oauth2callback', methods = ['POST'])
def oauth2callback():
    incoming = request
    grant_token = incoming.form['code']
    if logging: print("Grant Token: {}".format(grant_token))
    response = Zoho.Authorization().oauth2callback(grant_token=grant_token)
    return response

@app.route('/hub', methods = ['POST'])
def slack_hub():
    data = request.form['payload']
    response = hub(data)
    return jsonify(response)

@app.route('/new', methods = ['POST'])
def new():
    incoming = request
    data = incoming.form
    response = new_opportunity(data)
    return "success"

@app.route('/assign', methods = ['POST'])
def assign():
    incoming = request
    data = incoming.form
    response = assigned_opportunity(data['owner'],data['lead_id'])
    return "success"

if __name__ == '__main__':
    app.run()
