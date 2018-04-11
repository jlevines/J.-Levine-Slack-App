input_data = {
    'bot_token': 'xoxb-299198146754-XS7HBPydDnowTHjTQ8kxltVC',
    'auth': 'c9cfa32a490752dded5bfcc2e18e2189',
    'LeadId': '2817581000001557041'
}


__author__ = 'zpyoung'

######## Start Class Imports #############
import json
import uuid
import requests


class Conversation:
    def __init__(self,
                 target,
                 target_type="channel",
                 token=""):

        self.target = target
        self.target_type = target_type
        self.token = token

    def __str__(self):
        return "A object containing information for a Slack Conversation"

    def get_user_by_name (self, name):
        user_list = json.loads(requests.get(
            url="https://slack.com/api/users.list",
            params={
                "token": self.token
            }
        ).text)
        try:
            user_list = user_list["members"]
        except:
            raise ConversationError("Failed to get Users. Error: {}".format(user_list['error']))

        for member in user_list:
            if member["profile"]["real_name"]==name:
                return member["id"]
    def get_im(self, user):

        im_list = json.loads(requests.get(
            url="https://slack.com/api/im.open",
            params={
                "token": self.token,
                "user": user
            }
        ).text)
        try:
            return im_list["channel"]["id"]
        except:
            raise ConversationError("Failed to get IM. Error: {}".format(im_list['error']))

    def aim(self):

        if self.target_type == "channel":
            return self.target
        try:
            return self.get_im(self.target)
        except:
            try:
                return self.get_im(self.get_user_by_name(self.target))
            except:
                raise ConversationError("Failed to get IM. Error: {}".format(self.get_im(self.target)['error']))

    def post_message(self, message,
                     as_user=None,
                     icon_emoji=None,
                     icon_url=None,
                     link_names=None,
                     mrkdwn=None,
                     parse=None,
                     reply_broadcast=None,
                     unfurl_links=None,
                     unfurl_media=None,
                     username=None):

        params = message.built_message
        params.update({
            "channel": self.aim()
        })
        if as_user: params.update({"as_user": as_user})
        if icon_emoji: params.update({"icon_emoji": icon_emoji})
        if icon_url: params.update({"icon_url": icon_url})
        if link_names: params.update({"link_name": link_names})
        if mrkdwn: params.update({"mrkdwn": mrkdwn})
        if parse: params.update({"parse": parse})
        if reply_broadcast: params.update({"reply_broadcast": reply_broadcast})
        if unfurl_links: params.update({"unfurl_links": unfurl_links})
        if unfurl_media: params.update({"unfurl_media": unfurl_media})
        if username: params.update({"username": username})

        response = requests.post("https://slack.com/api/chat.postMessage", data=json.dumps(params),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer {}".format(self.token)})
        # noinspection PySimplifyBooleanCheck
        if json.loads(response.text)["ok"] == False:
            error = json.loads(response.text)["error"]
            raise PostMessageError("Slack Error: {}".format(error))

        return response


# noinspection PyAttributeOutsideInit
class Message:
    # A message sent to and displayed in a Slack Channel
    def __init__(self,
                 text="",
                 attachments=None,
                 thread_ts="",
                 response_type="in_channel",
                 replace_original=True,
                 delete_original=False,
                 destination=""):

        if not text and not attachments:
            raise BodyError("There is no text or attachment in this post.")

        self.text = slack_encode(text)
        self.attachments = attachments if attachments else []
        self.thread = thread_ts
        self.response = response_type
        self.replace = replace_original
        self.delete = delete_original
        self._destination = destination

    def __str__(self):
        return "A message sent to and displayed in a Slack Channel"

    @property
    def built_message(self):
        if self.text == "" and self.attachments == []:
            print('Please include a "text" or "attachment" in the Slack message.')
            pass
        built_message = {}
        if self.text != "":
            built_message.update({"text": self.text})
        if self.attachments:
            built_message.update({"attachments": self.attachments})
        if self.thread != "":
            built_message.update({"thread_ts": self.thread})
        built_message.update({"response_type": self.response})
        built_message.update({"replace_original": self.replace})
        built_message.update({"delete_original": self.delete})
        self._built_message = built_message
        return built_message

    def print_built(self):
        message = json.dumps(self.built_message)
        print("Built Message:\n{}".format(str(message)))

    def send(self):
        response = requests.post(self._destination, data=json.dumps(self.built_message))

        print("Response:{}".format(response))
        send_response = {
            "response": response,
            "response message": response.text,
            "response content": response.content
        }
        return send_response


class Attachment:
    # An attachment located in a Slack Message
    attachment_id = "Attachment ID: {}".format(str(uuid.uuid4())[:6])

    def __init__(self,
                 title="",
                 text="",
                 fallback="Error",
                 callback_id=attachment_id,
                 color="",
                 actions=None,
                 attachment_type="default",
                 pretext="",
                 author_name="",
                 author_link="",
                 author_icon="",
                 title_link="",
                 fields=None,
                 image_url="",
                 thumb_url="",
                 footer="",
                 footer_icon="",
                 ts=0
                 ):

        self.title = slack_encode(title)
        self.title_link = title_link
        self.image = image_url
        self.thumb = thumb_url
        self.text = slack_encode(text)
        self.pretext = slack_encode(pretext)
        self.fallback = fallback
        self.callback = callback_id
        self.color = color
        self.actions = actions if actions is not None else []
        self.type = attachment_type
        self.author = {
            "name": author_name,
            "link": author_link,
            "icon": author_icon
        }
        self.fields = fields if fields is not None else []
        self.footer = {
            "text": footer,
            "icon": footer_icon
        }
        self.ts = ts

    def __str__(self):
        return "An attachment located in a Slack Message"

    @property
    def built_message(self):
        built_message = {}
        if self.title != "":
            built_message.update({"title": self.title})
            if self.title_link != "":
                built_message.update({"title_link": self.title_link})
        if self.text != "":
            built_message.update({"text": self.text})
        if self.color != "":
            built_message.update({"color": self.color})
        if self.actions:
            built_message.update({"actions": self.actions})
        built_message.update({"fallback": self.fallback})
        built_message.update({"callback_id": self.callback})
        built_message.update({"attachment_type": self.type})
        if self.pretext != "":
            built_message.update({"pretext": self.pretext})
        if self.author["name"] != "":
            built_message.update({"author_name": self.author["name"]})
            if self.author["link"] != "":
                built_message.update({"author_link": self.author["link"]})
            if self.author["icon"] != "":
                built_message.update({"author_icon": self.author["icon"]})
        if self.fields:
            built_message.update({"fields": self.fields})
        if self.footer["text"] != "":
            built_message.update({"footer": self.footer["text"]})
            if self.footer["icon"] != "":
                built_message.update({"footer_icon": self.footer["icon"]})
        if self.ts != 0:
            built_message.update({"ts": self.ts})

        self._built_message = built_message
        return built_message

    def print_built(self):
        message = self.built_message
        print("Built Message:\n{}".format(str(message)))

    def new_field(self, title, value, short=False):
        field = {}
        if title:
            field.update({"title": title})
        if value:
            field.update({"value": slack_encode(value)})
        if short:
            field.update({"short": short})
        self.fields.append(field)


class Action:
    # An action located in a Slack Message Attachment
    action_id = "Action ID: {}".format(str(uuid.uuid4())[:6])

    # noinspection PyShadowingBuiltins
    def __init__(self,
                 name=action_id,
                 text="Text",
                 type="button",
                 value=None,
                 url=None,
                 confirm=None,
                 style=None,
                 options=None,
                 option_groups=None,
                 data_source=None,
                 selected_options=None,
                 min_query_length=0):

        self.name = slack_encode(name)
        self.text = text
        self.type = type
        self.value = value
        self.confirm = confirm if confirm else {}
        self.style = style
        self.options = options if options else []
        self.option_groups = option_groups if option_groups else []
        self.data_source = data_source
        self.selected_options = selected_options if selected_options else []
        self.min_query_length = min_query_length
        self.url = url

    def __str__(self):
        return "An action located in a Slack Message Attachment"

    @property
    def built_message(self):
        built_message = {
            "name": self.name,
            "text": self.text,
            "type": self.type
        }
        if self.value:
            built_message.update({"value": self.value})
        if self.url:
            built_message.update({"url": self.url})
        if self.confirm:
            built_message.update({"confirm": self.confirm})
        if self.style:
            built_message.update({"style": self.style})
        if self.options:
            built_message.update({"options": self.options})
        if self.option_groups:
            built_message.update({"option_groups": self.option_groups})
        if self.data_source:
            built_message.update({"data_source": self.data_source})
        if self.selected_options:
            built_message.update({"selected_options": self.selected_options})
        if self.min_query_length != 0:
            built_message.update({"min_query_length": self.min_query_length})
        self._built_message = built_message
        return built_message

    def print_built(self):
        message = self.built_message
        print("Built Message:\n{}".format(str(message)))

    def new_confirmation(self, title=None, text=None, ok_text=None, dismiss_text=None):
        if not title:
            print("Enter a title value for this confirmation.")
            return None
        confirmation = {"title": slack_encode(title)}
        if text:
            confirmation.update({"text": slack_encode(text)})
        if ok_text:
            confirmation.update({"ok_text": slack_encode(ok_text)})
        if dismiss_text:
            confirmation.update(({"dismiss_text": slack_encode(dismiss_text)}))
        self.confirm = confirmation

    def new_option(self, text, value, description=None):
        if not text or not value:
            print("Make sure text and value are input for this option.")
            pass
        option = {"text": text, "value": value}
        if description:
            option.update({"description": description})
        self.options.append(option)
        print("Option Created")
        return option

    def new_option_group(self, text, options):
        if not text:
            print("Enter a text value for this option group.")
            pass
        if not options:
            print("Enter a option values for this option group.")
            pass

        group = {"text": text, "options": options}
        self.option_groups.append(group)
        print("Option Group Created")


def slack_encode(text):
    keys = {
        "<": "&lt;",
        ">": "&gt;"
    }
    text = text.replace("&", "&amp;")
    for key in keys:
        text = text.replace(key, keys[key])
    return text


### Message Errors ###
class MessageError(Exception):
    def __init__(self, message):
        self.message = message


class BodyError(MessageError):
    pass


### Conversation Errors ###
class ConversationError(Exception):
    def __init__(self, message):
        self.message = message


class PostMessageError(ConversationError):
    pass
######## End Class Imports #############
### Start Zoho Import ##
def convert(stuff):
    dict = {}
    data = stuff["FL"]
    for item in data:
        dict.update({item["val"]: item["content"]})
    return dict


def Search(email, auth, module):
    url = "https://crm.zoho.com/crm/private/json/{module}/searchRecords".format(module = module)
    search = "(Email:{email})".format(email=email)
    parameter = {
        "authtoken": auth,
        "scope": "crmapi",
        "criteria": search
    }
    post = requests.get(url, params=parameter)
    if 'nodata' in json.loads(post.text)['response']:
        return "No Data"
    rows = json.loads(post.text)['response']['result'][module]['row']
    result=[]
    if isinstance(rows, list):
        for row in rows:
            result.append(convert(row))
    else:
        result = convert(rows)
    return result

def Get_Lead(id, auth):
    url = "https://crm.zoho.com/crm/private/json/Leads/getRecordById"
    params = {
        "authtoken": auth,
        "scope": "crmapi",
        "id":id
    }
    post = requests.get(url, params=params)
    result = convert(json.loads(post.text)['response']['result']['Leads']['row'])
    return result

def Lead_Check(leads, new_lead):
    stages=[
        "New - Unaccepted",
        "New - Accepted",
        "Contacting",
        "Appointment Set",
        "Long-Term Nurturing"
    ]
    if isinstance(leads, list):
        for lead in leads:
            if lead["Stage"] in stages and lead["LEADID"] != new_lead["LEADID"]:
                return True
        else:
            return False
    else:
        return False

def Update_Lead(id, xml_data, auth):
    url = "https://crm.zoho.com/crm/private/xml/Leads/updateRecords?"
    params = {
        "authtoken": auth,
        "scope": "crmapi",
        "id": id,
        "xmlData": xml_data
    }
    post = requests.post(url, params=params)
    return post

def xml_encode(map, module):
    values = ''
    for value in map:
        line = '<FL val="{key}">{entry}</FL>'.format(key = value, entry = map[value])
        values = values + line +'\n'
    xml = '''<{module}>
    <row no="1">
    {values}
    </row>
    </{module}>
    '''.format(module = module, values = values)
    return xml

def Get_Users(type, auth):
    url = "https://crm.zoho.com/crm/private/json/Users/getUsers"
    params = {
        "authtoken":auth,
        "scope":"crmapi",
        "type":type
    }
    post = requests.get(url,params=params)
    result = json.loads(post.text)["users"]["user"]
    return result
############ Start Code ############################
try:
    users = Get_Users(type="ActiveUsers", auth=input_data["auth"])
    lead_details = Get_Lead(id=input_data["LeadId"], auth=input_data["auth"])
    print ("Lead Details: {}\n".format(lead_details))

    if lead_details["Stage"]=="New - Unaccepted":
        reps = []
        for x in range(len(users)):
            if users[x]["role"] == "Sales Rep":
                reps.append(users[x])
        print("Reps: {}\n".format(reps))
        last_rep = Get_Lead(id='2817581000000164003', auth=input_data["auth"])["SMOWNERID"]
        print("Last Rep: {}\n".format(last_rep))
        new_rep = ""
        new_rep_name = ""
        for x in range(len(reps)):
            rep_id = reps[x]["id"]
            print("Rep ID: {}\n".format(rep_id))
            if rep_id == last_rep:
                new_rep = reps[0]["id"] if x == len(reps) - 1 else reps[x + 1]["id"]
                print("New Rep: {}\n".format(new_rep))
                new_rep_name = reps[0]["content"] if x == len(reps) - 1 else reps[x + 1]["content"]
                print("New Rep Name: {}\n".format(new_rep_name))
        xml = xml_encode({"SMOWNERID": new_rep},"Leads")
        print("XML: {}\n".format(xml))
        update_lead = Update_Lead(id=input_data["LeadId"],xml_data=xml,auth=input_data["auth"])
        print("Update Lead: {}\n".format(update_lead))
        update_cursor = Update_Lead(id='2817581000000164003',xml_data=xml,auth=input_data["auth"])
        print("Update Cursor: {}\n".format(update_cursor))

        formating = {
            "first_name": lead_details["First Name"] if "First Name" in lead_details else '',
            "last_name": lead_details["Last Name"] if "Last Name" in lead_details else '',
            "email": lead_details["Email"] if "Email" in lead_details else '',
            "phone": lead_details["Phone"] if "Phone" in lead_details else '',
            "main_inquiry": lead_details["Main Inquiry"] if "Main Inquiry" in lead_details else '',
            "id": input_data["LeadId"]}

        accept_button = Action(
            name="*1*accept*11*",
            text="Accept Opportunity",
            style="primary",
            type="button",
            value="*2*{email}*22**3*{id}*33*".format(**formating)
        )
        reject_button = Action(
            name="*1*deny*11*",
            text="Reject Opportunity",
            type="button",
            style="danger",
            value="*2*{email}*22**3*{id}*33*".format(**formating)
        )
        reject_button.new_confirmation("Are you sure?", "If you reject this opportunity, no one else will get it.",
                                       "Yes", "No")

        rr_attachment = Attachment(
            text="Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMain Inquiry: {main_inquiry}".format(
                **formating),
            fallback="Opportunity data failed to load.",
            callback_id="new_opp",
            color="#3AA3E3",
            attachment_type="default",
            actions=[accept_button.built_message, reject_button.built_message]
        )

        rr_message = Message(
            text="A new Opportunity has been assigned to you!",
            attachments=[rr_attachment.built_message]
        )

        convo = Conversation(new_rep_name, target_type="user", token=input_data["bot_token"])

        print(new_rep_name)
        print(convo.get_user_by_name(new_rep_name))
        print(convo.aim())

        response = convo.post_message(rr_message)

        followup_map = {
            "id": input_data["LeadId"]
        }
        followup = requests.post("https://hooks.zapier.com/hooks/catch/1593318/8p32n0/", data=followup_map)

        output = {"Completion": "Done"}
except KeyError:
    print("KeyError given: {}".format(KeyError.message))