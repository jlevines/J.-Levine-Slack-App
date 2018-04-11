import time

from decouple import config

from src.common.settings import testing, logging
from src.models import zoho_crm as Zoho
from src.common.util import assign_opportunity

from src.models.slack import Conversation


def opp_followup(ts:str, id:str, delay_min:int=15):
    if logging: print("opp_followup started")

    minutes_to_sleep = 2 if testing else delay_min
    time.sleep(minutes_to_sleep*60)

    lead = Zoho.Record("Leads").get_record(id)
    if lead["Stage"] == "New - Unaccepted":
        assign_response = assign_opportunity(id, followup=True, followup_ts=ts)
        opp_followup(
            ts=assign_response.json()['ts'],
            id=id
        )
        return "reassigned successfully"
    return "followup complete"



