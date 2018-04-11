
def new_opportunity(data):
    from src.common.settings import testing, logging
    from src.common.util import duplicate_record_check, assign_opportunity
    from src.models import zoho_crm as Zoho
    from src.logic.Opportunity_Followup import opp_followup

    if logging: print("new_opportunity started")

    lead_id = data["lead_id"]

    duplicate_record = duplicate_record_check("Leads", lead_id)
    if duplicate_record and not testing:
        assign_rep = Zoho.Record("Leads").update(lead_id, [{"Owner": {"id": duplicate_record["Owner"]["id"]}}])
        print("Rep Assigned:\n{}\n{}".format(assign_rep, assign_rep.text))
        return "Success"

    existing_consignor = duplicate_record_check("Contacts", lead_id, "Leads")
    if existing_consignor and not testing:
        assign_rep = Zoho.Record("Leads").update(lead_id, [{"Owner": {"id": existing_consignor["Owner"]["id"]}}])
        print("Rep Assigned:\n{}\n{}".format(assign_rep, assign_rep.text))
        return "Success"

    response = assign_opportunity(lead_id=lead_id)
    followup = opp_followup(
        ts=response.json()['ts'],
        id=lead_id
    )
    if logging: print("Followup: {}".format(followup))

    if logging: print("new_opportunity ended")
    return response
