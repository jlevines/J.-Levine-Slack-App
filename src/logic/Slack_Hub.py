def hub(data):
    from decouple import config

    from src.json import Opportunity_Accepted, Opportunity_Rejected, Opportunity_Junked
    import json
    from src.models.zoho_crm import Record
    from src.common.util import get_from_fields

    data=json.loads(data)
    value = json.loads(data['actions'][0]['value'].replace("'",'"'))
    target = data['user']['id']
    bot_token = config("Slackbot_Token", cast=str)
    name = get_from_fields('Name', data)

    # Interactive Messages
    # -------------------------
    if data["type"] == "interactive_message":
        if value['status'] == 'accepted':
            phone = get_from_fields('Phone', data)
            email = get_from_fields('Email', data)
            main = get_from_fields('Main', data)
            update = Record('Leads').update(id=value['lead_id'],
                                   data=[{
                                       'Stage': 'New - Accepted'
                                   }])
            response = Opportunity_Accepted.message(
                name=name,
                phone=phone,
                email=email,
                main=main,
                id=value['lead_id']
            )
            return response

        if value['status'] == 'rejected':
            response = Opportunity_Rejected.message(
                name=name
            )
            return response

        if value['status'] == 'junk':
            update = Record('Leads').update(id=value['lead_id'],
                                   data=[{
                                       'Stage': 'Abandoned',
                                       'Lead Status': 'Inactive'
                                   }]
                                   )
            response = Opportunity_Junked.message(
                name=name
            )
            return response
