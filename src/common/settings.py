from decouple import config
from src.models import zoho_crm as Zoho

testing = config("Local_Development", cast=bool)
logging = config("Logging", cast=bool)
test_user = Zoho.Users(id="2817581000000131011").get_user()