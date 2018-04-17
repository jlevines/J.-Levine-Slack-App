import os

from decouple import config

from src.common.settings import testing, test_user, logging
from src.models import zoho_crm as Zoho
from src.models.slack import Conversation
from src.json.New_Opportuntiy_Message import message as new_opp_message
from src.json.Opportunity_Expired import message as expired_message


def duplicate_record_check(search_module: str, existing_id: str, existing_module: str = None):
    existing_module = existing_module if existing_module else search_module
    if logging: print(
        "Duplicate_record_check started for {} - {} in {}".format(existing_module, existing_id, search_module))

    lead_details = Zoho.Record(existing_module).get_record(existing_id)
    search_results = None

    if "Email" in lead_details:
        search_results = Zoho.Record(search_module).search(email=lead_details["Email"])
    if "Phone" in lead_details:
        search_results = Zoho.Record(search_module).search(phone=lead_details["Phone"])
    if logging:
        if search_results:
            print("Duplicate record for {} - {} found".format(search_module, existing_id))
        else:
            print("No duplicate record for {} - {} found".format(search_module, existing_id))

    if logging: print("Duplicate_record_check ended for {} - {}".format(search_module, existing_id))

    return search_results


def round_robin(user_list: list, last_user: str):
    if logging: print("round_robin started")

    new_user = None
    for x in range(len(user_list)):
        if last_user in user_list[x]:
            new_user = user_list[x + 1]
            if logging: print("New User:\n{}".format(new_user))

    if logging: print("round_robin ended")
    return new_user


def get_user_by_role(role: str, type: str = "ActiveUsers") -> list:
    if logging: print("get_user_by_role started")

    users = Zoho.Users().list_users(type)
    role_users = []
    for user in users:
        if role == user["role"]["name"]:
            role_users.append(user)

    if logging: print("{} Users:\n{}".format(role, role_users))
    if logging: print("get_user_by_role ended")

    return role_users


def assign_opportunity(lead_id: str, followup: bool = False, followup_ts: str = None, followup_channel: str = None):
    sales_reps = get_user_by_role("Sales Rep")
    last_owner = config("Last_Owner", cast=str)
    new_owner = round_robin(sales_reps, last_owner) if not testing else test_user
    lead_details = Zoho.Record("Leads").get_record(lead_id)
    bot_token = config("Slackbot_Token", cast=str)

    assign_rep = Zoho.Record("Leads").update(lead_id, [{"Owner": {"id": new_owner["id"]}}])

    os.environ["Last_Owner"] = new_owner["id"]
    if logging: print("Last_Owner environmental variable set")

    new_owner_name = "{} {}".format(new_owner["first_name"], new_owner["last_name"])
    convo = Conversation(new_owner_name, target_type="user", token=bot_token)
    if logging: print("New Owner Name: {}".format(new_owner_name))

    lead_name = "{}{}".format("{} ".format(lead_details["First_Name"]) if "First_Name" in lead_details else "",
                              lead_details["Last_Name"])
    response = convo.post_message(new_opp_message(
        name=lead_name,
        email=lead_details["Email"],
        phone=lead_details["Phone"],
        main=lead_details["Main_Inquiry"],
        id=lead_id
    ))
    if logging: print("Slack Target: {}".format(convo.aim()))

    if followup:
        last_owner_data = Zoho.Users(id=last_owner).get_user()
        last_owner_name = "{} {}".format(last_owner_data["first_name"], last_owner_data["last_name"])
        timeout_convo = Conversation(last_owner_name, target_type="user", token=bot_token)
        update = timeout_convo.update_message(channel=followup_channel,ts=followup_ts,attachments=[expired_message(lead_name)]).json()
        new_ts=response.json()['ts']
        return new_ts

    return response


def get_from_fields(field, data, search_type='title', return_type='value'):
    try:
        fields = data['original_message']['attachments'][0]['fields']
        for x in fields:
            if field in x[search_type]:
                return x[return_type]
    except:
        return None