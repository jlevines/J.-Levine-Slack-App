import time

from decouple import config

from src.common.settings import testing, logging
from src.models import zoho_crm as Zoho
from src.common.util import assign_opportunity

from src.models.slack import Conversation


def opp_followup(ts: str, id: str, channel: str, delay_min: int = 15):
    if logging: print("opp_followup started")

    minutes_to_sleep = 1 if testing else delay_min

    lead = Zoho.Record("Leads").get_record(id)

    while lead["Stage"] == "New - Unaccepted":

        for x in range(0, minutes_to_sleep):
            time.sleep(60)
            if (x + 1) % 3 == 0:
                lead = Zoho.Record("Leads").get_record(id)
                if lead["Stage"] == "New - Unaccepted":
                    print("Lead still Unaccepted")
                else:
                    return "followup complete"
        lead = Zoho.Record("Leads").get_record(id)
        if lead["Stage"] == "New - Unaccepted":
            ts = assign_opportunity(id, followup=True, followup_ts=ts, followup_channel=channel)
            print("reassigned successfully")

    return "followup complete"
