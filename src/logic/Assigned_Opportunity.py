__author__ = 'zpyoung'

from src.models.slack import Conversation
from src.json.New_Opportuntiy_Message import message as new_opp_message
from src.models import zoho_crm as Zoho
from decouple import config
from src.logic.Opportunity_Followup import opp_followup
from src.common.settings import testing, logging

def assigned_opportunity(owner,lead_id):
    if logging: print("**************************\nassigned_opportunity started")
    bot_token = config("Slackbot_Token", cast=str)
    lead_details = Zoho.Record("Leads").get_record(lead_id)
    lead_name = "{}{}".format("{} ".format(lead_details["First_Name"]) if "First_Name" in lead_details else "",
                              lead_details["Last_Name"])

    convo = Conversation(owner, target_type="user", token=bot_token)

    response = convo.post_message(new_opp_message(
        name=lead_name,
        email=lead_details["Email"],
        phone=lead_details["Phone"],
        main=lead_details["Main_Inquiry"],
        id=lead_id
    ))
    followup = opp_followup(
        ts=response.json()['ts'],
        id=lead_id,
        channel=response.json()['channel']
    )
    if logging: print("Followup: {}".format(followup))
    if logging: print("assigned_opportunity ended\n**************************")
    pass